import imglyb
from imglyb import util
from jnius import autoclass, cast

import ctypes
import numpy as np

Intervals = autoclass('net.imglib2.util.Intervals')

dtype_selector = {
    'FloatType': np.dtype('float32'),
    'DoubleType': np.dtype('float64'),
    'ByteType': np.dtype('int8'),
    'UnsignedByteType': np.dtype('uint8'),
    'ShortType': np.dtype('int16'),
    'UnsignedShortType': np.dtype('uint16'),
    'IntType': np.dtype('int32'),
    'UnsignedIntType': np.dtype('uint32'),
    'LongType': np.dtype('int64'),
    'UnsignedLongType': np.dtype('uint64'),
}

ctype_conversions_imglib = {
    'FloatType': ctypes.c_float,
    'DoubleType': ctypes.c_double,
    'ByteType': ctypes.c_int8,
    'UnsignedByteType': ctypes.c_uint8,
    'ShortType': ctypes.c_int16,
    'UnsignedShortType': ctypes.c_uint16,
    'IntType': ctypes.c_int32,
    'UnsignedIntType': ctypes.c_uint32,
    'LongType': ctypes.c_int64,
    'UnsignedLongType': ctypes.c_uint64
}


def get_address(rai):
    class_name = util.Helpers.classNameSimple(rai)
    class_name_full = util.Helpers.className(rai)
    if class_name in ('ArrayImg', 'UnsafeImg'):
        access = cast(class_name_full, rai).update(None)
        access_type = util.Helpers.className(access)

        if 'basictypelongaccess.unsafe' in access_type:
            return cast(access_type, access).getAddress()
        else:
            raise ValueError("Excpected unsafe access but got {}".format(access_type))

    else:
        raise ValueError("Excpected ArrayImg or UnsafeImg but got {}".format(class_name))


class ImgLibReferenceGuard(np.ndarray):
    def __new__(cls, rai):
        access = rai.randomAccess()
        rai.min(access)
        imglib_type = util.Helpers.classNameSimple(access.get())
        address = get_address(rai)

        shape = tuple(Intervals.dimensionsAsLongArray(rai))[::-1]
        dtype = dtype_selector[imglib_type]
        pointer = ctypes.cast(address, ctypes.POINTER(ctype_conversions_imglib[imglib_type]))
        order = 'C'

        obj = np.ndarray.__new__(cls, buffer=np.ctypeslib.as_array(pointer, shape=shape), shape=shape, dtype=dtype)
        obj.setflags(write=True)
        obj.rai = rai
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.rai = obj.rai


if __name__ == "__main__":

    ArrayImgs = autoclass('net.imglib2.img.array.ArrayImgs')
    UnsafeUtil = autoclass('net.imglib2.img.basictypelongaccess.unsafe.UnsafeUtil')
    Arrays = autoclass('java.util.Arrays')
    OwningFloatUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.owning.OwningFloatUnsafe')
    Fraction = autoclass('net.imglib2.util.Fraction')
    LongStream = autoclass('java.util.stream.LongStream')

    shape = (2, 3, 4)
    n_elements = int(np.prod(shape))
    data_store = OwningFloatUnsafe(n_elements)
    dim_array = LongStream.of(*shape).toArray()
    print(Arrays.toString(dim_array))
    rai = util.Helpers.toArrayImg(cast(util.Helpers.className(data_store), data_store), dim_array)
    # rai = ArrayImgs.floats( *shape )
    c = rai.cursor()
    count = 23
    while c.hasNext():
        c.next().setReal(count)
        count += 1
    print(util.Helpers.className(rai.randomAccess().get()))
    print(util.Helpers.classNameSimple(rai.randomAccess().get()))
    arr = ImgLibReferenceGuard(rai)
    print(arr, arr.mean())
    c = rai.cursor()
    c.fwd()
    c.next().setReal(0)
    print(arr, arr.mean())
