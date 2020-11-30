import logging
import math
import numpy as np
import scyjava

from jpype import JException, JImplements, JOverride

from . import accesses
from . import caches
from . import types
from . import util
from .reference_store import ReferenceStore


_global_reference_store = ReferenceStore()

_logger = logging.getLogger(__name__)

def _java_setup():
    """
    Lazy initialization function for Java-dependent data structures.
    Do not call this directly; use scyjava.start_jvm() instead.
    """
    global PythonHelpers
    PythonHelpers = scyjava.jimport('net.imglib2.python.Helpers')

    # non-owning
    global _ByteUnsafe
    _ByteUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
    global _CharUnsafe
    _CharUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
    global _DoubleUnsafe
    _DoubleUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
    global _FloatUnsafe
    _FloatUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
    global _IntUnsafe
    _IntUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
    global _LongUnsafe
    _LongUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
    global _ShortUnsafe
    _ShortUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')

    global _unsafe_for_dtype
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
    global _OwningByteUnsafe
    _OwningByteUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningByteUnsafe')
    global _OwningCharUnsafe
    _OwningCharUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningCharUnsafe')
    global _OwningDoubleUnsafe
    _OwningDoubleUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningDoubleUnsafe')
    global _OwningFloatUnsafe
    _OwningFloatUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningFloatUnsafe')
    global _OwningIntUnsafe
    _OwningIntUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningIntUnsafe')
    global _OwningLongUnsafe
    _OwningLongUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningLongUnsafe')
    global _OwningShortUnsafe
    _OwningShortUnsafe = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningShortUnsafe')

    global _unsafe_owning_for_dtype
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

    global MakeAccessFunction
    @JImplements('java.util.function.LongFunction')
    class MakeAccessFunction():
        """
        Implements a java `LongFunction` that can be passed into `PythonHelpers.imgFromFunc` and
        `PythonHelpers.imgWithCellLoaderFromFunc`.
        """

        def __init__(self, func):
            self.func = func

        @JOverride
        def apply(self, index):
            access = self.func(index)
            return access

scyjava.when_jvm_starts(_java_setup)


def identity(x):
    """
    Returns the input
    """
    return x


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
        dtype = types.for_np_dtype(chunk.dtype, volatile=False)
        ptype = dtype.getNativeTypeFactory().getPrimitiveType()
        # TODO check ratio for integral value first?
        ratio = int(dtype.getEntitiesPerPixel().getRatio())
        return accesses.Accesses.asArrayAccess(
            util._get_address(chunk),
            chunk.size * ratio,
            use_volatile_access,
            ptype)

    except JException as e:
        _logger.error(scyjava.jstacktrace(e))
        raise e


def _get_chunk_access_unsafe(array, chunk_shape, index, chunk_as_array, reference_store):

    try:
        chunk = np.ascontiguousarray(_get_chunk(array, chunk_shape, index, chunk_as_array))
        address = util._get_address(chunk)
        ref_id = reference_store.get_next_id()

        def remove_reference():
            _logger.debug('Removing ref id %d', ref_id)
            reference_store.remove_reference(ref_id)
        owner = util.RunnableFromFunc(remove_reference)
        reference_store.add_reference(ref_id, (chunk, owner))
        access = _access_factory_for(chunk.dtype, owning=False)(address, owner)
        return access

    except JException as e:
        _logger.error(scyjava.jstacktrace(e))
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
    scyjava.start_jvm()

    access_type_function_mapping = {
        'array':  as_cell_img_with_array_accesses,
        'native': as_cell_img_with_native_accesses
    }

    if access_type not in access_type_function_mapping:
        raise Exception(f'Invalid access type: `{access_type}\'. Choose one of {access_type_function_mapping.keys()}')

    cache = caches.BoundedSoftRefLoaderCache(cache) if isinstance(cache, int) else cache

    return access_type_function_mapping[access_type](array, chunk_shape, chunk_as_array, cache, **kwargs)


# TODO is it bad style to use **kwargs to ignore unexpected kwargs?
def as_cell_img_with_array_accesses(array, chunk_shape, chunk_as_array, cache, *, use_volatile_access=True, **kwargs):
    scyjava.start_jvm()

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
    scyjava.start_jvm()

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

    except JException as e:
        _logger.error(jstacktrace(e))
        raise e

    return img, reference_store


def _access_factory_for(dtype, owning):
    return _unsafe_owning_for_dtype[dtype] if owning else _unsafe_for_dtype[dtype]


