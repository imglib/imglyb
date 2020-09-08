import numpy as np
import jpype
import jpype.imports

Accesses            = jpype.JClass('net.imglib2.img.basictypeaccess.Accesses')

ByteArray           = jpype.JClass('net.imglib2.img.basictypeaccess.array.ByteArray')
CharArray           = jpype.JClass('net.imglib2.img.basictypeaccess.array.CharArray')
DoubleArray         = jpype.JClass('net.imglib2.img.basictypeaccess.array.DoubleArray')
FloatArray          = jpype.JClass('net.imglib2.img.basictypeaccess.array.FloatArray')
IntArray            = jpype.JClass('net.imglib2.img.basictypeaccess.array.IntArray')
LongArray           = jpype.JClass('net.imglib2.img.basictypeaccess.array.LongArray')
ShortArray          = jpype.JClass('net.imglib2.img.basictypeaccess.array.ShortArray')

VolatileByteArray   = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileByteArray')
VolatileCharArray   = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileCharArray')
VolatileDoubleArray = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileDoubleArray')
VolatileFloatArray  = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileFloatArray')
VolatileIntArray    = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileIntArray')
VolatileLongArray   = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileLongArray')
VolatileShortArray  = jpype.JClass('net.imglib2.img.basictypeaccess.volatiles.array.VolatileShortArray')

ByteUnsafe          = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
CharUnsafe          = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
DoubleUnsafe        = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
FloatUnsafe         = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
IntUnsafe           = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
LongUnsafe          = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
ShortUnsafe         = jpype.JClass('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')


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

