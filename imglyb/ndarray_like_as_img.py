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

Accesses = autoclass('tmp.net.imglib2.img.basictypeaccess.Accesses')
PythonHelpers = autoclass('net.imglib2.python.Helpers')

_global_reference_store = ReferenceStore()

_logger = logging.getLogger(__name__)


def identity(x):
    return x


class MakeAccessFunction(PythonJavaClass):
    __javainterfaces__ = ['java/util/function/LongFunction']

    def __init__(self, func):
        super(MakeAccessFunction, self).__init__()
        self.func = func

    @java_method('(J)Ljava/lang/Object;')
    def apply(self, index):
        access = self.func(index)
        return access


def chunk_index_to_slices(shape, chunk_shape, cell_index):

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


def get_chunk(array, chunk_shape, chunk_index, chunk_as_array):
    slices = chunk_index_to_slices(array.shape, chunk_shape, chunk_index)
    sliced = array[slices]
    array = chunk_as_array(sliced)
    return np.ascontiguousarray(array)


def get_chunk_access_array(array, chunk_shape, index, chunk_as_array, use_volatile_access=True):
    try:
        chunk = get_chunk(array, chunk_shape, index, chunk_as_array)
        dtype = for_np_dtype(chunk.dtype, volatile=False)
        ptype = dtype.getNativeTypeFactory().getPrimitiveType()
        # TODO check ratio for integral value first?
        ratio = int(dtype.getEntitiesPerPixel().getRatio())
        return Accesses.asArrayAccess(
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


def get_chunk_access_unsafe(array, chunk_shape, index, chunk_as_array, reference_store):

    try:
        chunk = np.ascontiguousarray(get_chunk(array, chunk_shape, index, chunk_as_array))
        address = _get_address(chunk)
        ref_id = reference_store.get_next_id()

        def remove_reference():
            _logger.debug('Removing ref id %d', ref_id)
            reference_store.remove_reference(ref_id)
        owner = RunnableFromFunc(remove_reference)
        reference_store.add_reference(ref_id, (chunk, owner))
        access = access_factory_for(chunk.dtype, owning=False)(address, owner)
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
        lambda index: get_chunk_access_array(array, chunk_shape, index, chunk_as_array, use_volatile_access=use_volatile_access))
    reference_store = ReferenceStore()
    reference_store.add_reference_with_new_id(access_generator)

    shape = array.shape[::-1]
    chunk_shape = chunk_shape[::-1]

    img = PythonHelpers.imgWithCellLoaderFromFunc(
        shape,
        chunk_shape,
        access_generator,
        types.for_np_dtype(array.dtype, volatile=False),
        # TODO do not load first block here, just create a length-one access
        accesses.as_array_access(
            get_chunk(array, chunk_shape, 0, chunk_as_array=chunk_as_array),
            volatile=use_volatile_access),
        cache)

    return img, reference_store


# TODO is it bad style to use **kwargs to ignore unexpected kwargs?
def as_cell_img_with_native_accesses(array, chunk_shape, chunk_as_array, cache, **kwargs):

    reference_store = ReferenceStore()
    access_generator = MakeAccessFunction(
        lambda index: get_chunk_access_unsafe(array, chunk_shape, index, chunk_as_array, reference_store))
    reference_store.add_reference_with_new_id(access_generator)

    shape = array.shape[::-1]
    chunk_shape = chunk_shape[::-1]

    try:
        img = PythonHelpers.imgFromFunc(
            shape,
            chunk_shape,
            access_generator,
            types.for_np_dtype(array.dtype, volatile=False),
            access_factory_for(array.dtype, owning=False)(1, None),
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
ByteUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
CharUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
DoubleUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
FloatUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
IntUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
LongUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
ShortUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')


def access_factory_for(dtype, owning):
    return unsafe_owning_for_dtype[dtype] if owning else unsafe_for_dtype[dtype]


unsafe_for_dtype = {
    np.dtype('complex64')  : FloatUnsafe,
    np.dtype('complex128') : DoubleUnsafe,
    np.dtype('float32')    : FloatUnsafe,
    np.dtype('float64')    : DoubleUnsafe,
    np.dtype('int8')       : ByteUnsafe,
    np.dtype('int16')      : ShortUnsafe,
    np.dtype('int32')      : IntUnsafe,
    np.dtype('int64')      : LongUnsafe,
    np.dtype('uint8')      : ByteUnsafe,
    np.dtype('uint16')     : ShortUnsafe,
    np.dtype('uint32')     : IntUnsafe,
    np.dtype('uint64')     : LongUnsafe
}

# owning
OwningByteUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningByteUnsafe')
OwningCharUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningCharUnsafe')
OwningDoubleUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningDoubleUnsafe')
OwningFloatUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningFloatUnsafe')
OwningIntUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningIntUnsafe')
OwningLongUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningLongUnsafe')
OwningShortUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningShortUnsafe')

unsafe_owning_for_dtype = {
    np.dtype('complex64')  : lambda size: OwningFloatUnsafe(2 * size),
    np.dtype('complex128') : lambda size: OwningDoubleUnsafe(2 * size),
    np.dtype('float32')    : OwningFloatUnsafe,
    np.dtype('float64')    : OwningDoubleUnsafe,
    np.dtype('int8')       : OwningByteUnsafe,
    np.dtype('int16')      : OwningShortUnsafe,
    np.dtype('int32')      : OwningIntUnsafe,
    np.dtype('int64')      : OwningLongUnsafe,
    np.dtype('uint8')      : OwningByteUnsafe,
    np.dtype('uint16')     : OwningShortUnsafe,
    np.dtype('uint32')     : OwningIntUnsafe,
    np.dtype('uint64')     : OwningLongUnsafe
}
