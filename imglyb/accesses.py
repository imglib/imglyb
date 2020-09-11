import numpy as np
from jpype import JClass

Accesses            = JClass('net.imglib2.img.basictypeaccess.Accesses')

ByteArray           = JClass('net.imglib2.img.basictypeaccess.array.ByteArray')
CharArray           = JClass('net.imglib2.img.basictypeaccess.array.CharArray')
DoubleArray         = JClass('net.imglib2.img.basictypeaccess.array.DoubleArray')
FloatArray          = JClass('net.imglib2.img.basictypeaccess.array.FloatArray')
IntArray            = JClass('net.imglib2.img.basictypeaccess.array.IntArray')
LongArray           = JClass('net.imglib2.img.basictypeaccess.array.LongArray')
ShortArray          = JClass('net.imglib2.img.basictypeaccess.array.ShortArray')

VolatileByteArray   = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileByteArray')
VolatileCharArray   = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileCharArray')
VolatileDoubleArray = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileDoubleArray')
VolatileFloatArray  = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileFloatArray')
VolatileIntArray    = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileIntArray')
VolatileLongArray   = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileLongArray')
VolatileShortArray  = JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileShortArray')

ByteUnsafe          = JClass('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
CharUnsafe          = JClass('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
DoubleUnsafe        = JClass('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
FloatUnsafe         = JClass('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
IntUnsafe           = JClass('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
LongUnsafe          = JClass('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
ShortUnsafe         = JClass('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')


# does not work with strided accesses, currently
def as_array_access(ndarray, volatile=False):
    if ndarray.dtype == np.uint8 or ndarray.dtype == np.int8:
        return _as_array_access(ndarray, ByteUnsafe, lambda n : VolatileByteArray(n, True) if volatile else ByteArray(n))
    elif ndarray.dtype == np.uint16 or ndarray.dtype == np.int16:
        return _as_array_access(ndarray, ShortUnsafe, lambda n : VolatileShortArray(n, True) if volatile else ShortArray(n))
    elif ndarray.dtype == np.uint32 or ndarray.dtype == np.int32:
        return _as_array_access(ndarray, IntUnsafe, lambda n : VolatileIntArray(n, True) if volatile else IntArray(n))
    elif ndarray.dtype == np.uint64 or ndarray.dtype == np.int64:
        return _as_array_access(ndarray, LongUnsafe, lambda n : VolatileLongArray(n, True) if volatile else LongArray(n))
    elif ndarray.dtype == np.float32:
        return _as_array_access(ndarray, FloatUnsafe, lambda n : VolatileFloatArray(n, True) if volatile else FloatArray(n))
    elif ndarray.dtype == np.float64:
        return _as_array_access(ndarray, DoubleUnsafe, lambda n : VolatileDoubleArray(n, True) if volatile else DoubleArray(n))


def _as_array_access(ndarray, src_clazz, tgt_clazz):
    src = src_clazz(ndarray.ctypes.data)
    tgt = tgt_clazz(ndarray.size)
    Accesses.copyAny(src, 0, tgt, 0, ndarray.size)
    return tgt

