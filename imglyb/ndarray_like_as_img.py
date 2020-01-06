import logging
import math
import numpy as np

from . import accesses
from . import types
from .caches import BoundedSoftRefLoaderCache
from .reference_store import ReferenceStore
from .types import for_np_dtype
from .util import RunnableFromFunc, _get_address
from jnius import JavaException, autoclass, PythonJavaClass, java_method

PythonHelpers = autoclass('net.imglib2.python.Helpers')

_global_reference_store = ReferenceStore()

_logger = logging.getLogger(__name__)


def identity(x):
    """
    Returns the input
    """
    return x


class MakeAccessFunction(PythonJavaClass):
    """
    Implements a java `LongFunction` that can be passed into `PythonHelpers.imgFromFunc` and
    `PythonHelpers.imgWithCellLoaderFromFunc`.
    """
    __javainterfaces__ = ['java/util/function/LongFunction']

    def __init__(self, func):
        super(MakeAccessFunction, self).__init__()
        self.func = func

    @java_method('(J)Ljava/lang/Object;')
    def apply(self, index):
        access = self.func(index)
        return access


def _chunk_index_to_slices(shape, chunk_shape, cell_index):

    grid_dimensions = tuple(
        int(math.ceil(s/sh))
        for s, sh in zip(shape, chunk_shape))[::-1]

    chunk_min = []
    ndims = len(grid_dimensions)

    i = cell_index
    for d in range(ndims):
        c = i % grid_dimensions[d]
        chunk_min.append(c)
        i = (i - c)//grid_dimensions[d]

    chunk_min = chunk_min[::-1]

    slices = tuple(
        slice(c*cs, (c + 1)*cs)
        for c, cs in zip(chunk_min, chunk_shape))

    return slices


def _get_chunk(array, chunk_shape, chunk_index, chunk_as_array):
    slices = _chunk_index_to_slices(array.shape, chunk_shape, chunk_index)
    sliced = array[slices]
    array = chunk_as_array(sliced)
    return np.ascontiguousarray(array)


def _get_chunk_access_array(array, chunk_shape, index, chunk_as_array, use_volatile_access=True):
    try:
        chunk = _get_chunk(array, chunk_shape, index, chunk_as_array)
        dtype = for_np_dtype(chunk.dtype, volatile=False)
        ptype = dtype.getNativeTypeFactory().getPrimitiveType()
        # TODO check ratio for integral value first?
        ratio = int(dtype.getEntitiesPerPixel().getRatio())
        return accesses.Accesses.asArrayAccess(
            _get_address(chunk),
            chunk.size * ratio,
            use_volatile_access,
            ptype)

    except JavaException as e:
        print("exception    ", e)
        print("cause        ", e.__cause__)
        print("inner message", e.innermessage)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e


def _get_chunk_access_unsafe(array, chunk_shape, index, chunk_as_array, reference_store):

    try:
        chunk = np.ascontiguousarray(_get_chunk(array, chunk_shape, index, chunk_as_array))
        address = _get_address(chunk)
        ref_id = reference_store.get_next_id()

        def remove_reference():
            _logger.debug('Removing ref id %d', ref_id)
            reference_store.remove_reference(ref_id)
        owner = RunnableFromFunc(remove_reference)
        reference_store.add_reference(ref_id, (chunk, owner))
        access = _access_factory_for(chunk.dtype, owning=False)(address, owner)
        return access

    except JavaException as e:
        print("exception    ", e)
        print("cause        ", e.__cause__)
        print("inner message", e.innermessage)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e


def as_cell_img(array, chunk_shape, cache, *, access_type='native', chunk_as_array=identity, **kwargs):
    """
    Wrap an arbitrary ndarray-like object as an ImgLib2 cached cell img.

    :param array: The arbitrary ndarray-like object to be wrapped
    :param chunk_shape: The shape of `array`. In many cases, this is just `array.shape`.
    :param cache: Can be `int` or an ImgLib2 `LoaderCache`. If `int` (recommended), use a
                :py:data:`imglyb.caches.BoundedSoftRefLoaderCache` that is bounded to `cache` elements.
                `LoaderCache`s are available in :py:mod:`imglyb.caches`.
    :param access_type: Can be either `'native'` or `'array'`. If `'native'`, use the native memory of the contiguous
                ndarray of a chunk directly. If `'array'`, copy the native memory into a Java array and use the Java
                array as access.
    :param chunk_as_array: Defines conversion of a chunk created by slicing into a :py:class:`numpy.ndarray`.
    :param kwargs: Optional arguments that may depend on the value passed for `access_type`, e.g `use_volatile_access`
                is relevant only for `access_type == 'array'`.
    :return: A tuple that holds the wrapped image at `0` and a reference store at `1` to ensure that Python references
                are not being garbage collected while still in use in the JVM. the reference store should stay in scope
                as long as the wrapped image is intended to be used.
    """
    access_type_function_mapping = {
        'array':  as_cell_img_with_array_accesses,
        'native': as_cell_img_with_native_accesses
    }

    if access_type not in access_type_function_mapping:
        raise Exception(f'Invalid access type: `{access_type}\'. Choose one of {access_type_function_mapping.keys()}')

    cache = BoundedSoftRefLoaderCache(cache) if isinstance(cache, int) else cache

    return access_type_function_mapping[access_type](array, chunk_shape, chunk_as_array, cache, **kwargs)


# TODO is it bad style to use **kwargs to ignore unexpected kwargs?
def as_cell_img_with_array_accesses(array, chunk_shape, chunk_as_array, cache, *, use_volatile_access=True, **kwargs):
    access_generator = MakeAccessFunction(
        lambda index: _get_chunk_access_array(array, chunk_shape, index, chunk_as_array, use_volatile_access=use_volatile_access))
    reference_store = ReferenceStore()
    reference_store.add_reference_with_new_id(access_generator)

    shape = array.shape[::-1]
    chunk_shape = chunk_shape[::-1]

    # TODO use imgFromFunc instead of imgWithCellLoaderFromFunct here
    img = PythonHelpers.imgWithCellLoaderFromFunc(
        shape,
        chunk_shape,
        access_generator,
        types.for_np_dtype(array.dtype, volatile=False),
        # TODO do not load first block here, just create a length-one access
        accesses.as_array_access(
            _get_chunk(array, chunk_shape, 0, chunk_as_array=chunk_as_array),
            volatile=use_volatile_access),
        cache)

    return img, reference_store


# TODO is it bad style to use **kwargs to ignore unexpected kwargs?
def as_cell_img_with_native_accesses(array, chunk_shape, chunk_as_array, cache, **kwargs):

    reference_store = ReferenceStore()
    access_generator = MakeAccessFunction(
        lambda index: _get_chunk_access_unsafe(array, chunk_shape, index, chunk_as_array, reference_store))
    reference_store.add_reference_with_new_id(access_generator)

    shape = array.shape[::-1]
    chunk_shape = chunk_shape[::-1]

    try:
        img = PythonHelpers.imgFromFunc(
            shape,
            chunk_shape,
            access_generator,
            types.for_np_dtype(array.dtype, volatile=False),
            _access_factory_for(array.dtype, owning=False)(1, None),
            cache)

    except JavaException as e:
        print("exception    ", e)
        print("cause        ", e.__cause__)
        print("inner message", e.innermessage)
        print("stack trace  ", e.stacktrace)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e

    return img, reference_store

# non-owning
_ByteUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
_CharUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
_DoubleUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
_FloatUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
_IntUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
_LongUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
_ShortUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')


def _access_factory_for(dtype, owning):
    return _unsafe_owning_for_dtype[dtype] if owning else _unsafe_for_dtype[dtype]


_unsafe_for_dtype = {
    np.dtype('complex64')  : _FloatUnsafe,
    np.dtype('complex128') : _DoubleUnsafe,
    np.dtype('float32')    : _FloatUnsafe,
    np.dtype('float64')    : _DoubleUnsafe,
    np.dtype('int8')       : _ByteUnsafe,
    np.dtype('int16')      : _ShortUnsafe,
    np.dtype('int32')      : _IntUnsafe,
    np.dtype('int64')      : _LongUnsafe,
    np.dtype('uint8')      : _ByteUnsafe,
    np.dtype('uint16')     : _ShortUnsafe,
    np.dtype('uint32')     : _IntUnsafe,
    np.dtype('uint64')     : _LongUnsafe
}

# owning
_OwningByteUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningByteUnsafe')
_OwningCharUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningCharUnsafe')
_OwningDoubleUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningDoubleUnsafe')
_OwningFloatUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningFloatUnsafe')
_OwningIntUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningIntUnsafe')
_OwningLongUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningLongUnsafe')
_OwningShortUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningShortUnsafe')

_unsafe_owning_for_dtype = {
    np.dtype('complex64')  : lambda size: _OwningFloatUnsafe(2 * size),
    np.dtype('complex128') : lambda size: _OwningDoubleUnsafe(2 * size),
    np.dtype('float32')    : _OwningFloatUnsafe,
    np.dtype('float64')    : _OwningDoubleUnsafe,
    np.dtype('int8')       : _OwningByteUnsafe,
    np.dtype('int16')      : _OwningShortUnsafe,
    np.dtype('int32')      : _OwningIntUnsafe,
    np.dtype('int64')      : _OwningLongUnsafe,
    np.dtype('uint8')      : _OwningByteUnsafe,
    np.dtype('uint16')     : _OwningShortUnsafe,
    np.dtype('uint32')     : _OwningIntUnsafe,
    np.dtype('uint64')     : _OwningLongUnsafe
}
