import numpy as np
import scyjava

def _java_setup():
    """
    Lazy initialization function for Java-dependent data structures.
    Do not call this directly; use scyjava.start_jvm() instead.
    """

    global Accesses
    Accesses            = scyjava.jimport('net.imglib2.img.basictypeaccess.Accesses')

    global ByteArray
    ByteArray           = scyjava.jimport('net.imglib2.img.basictypeaccess.array.ByteArray')
    global CharArray
    CharArray           = scyjava.jimport('net.imglib2.img.basictypeaccess.array.CharArray')
    global DoubleArray
    DoubleArray         = scyjava.jimport('net.imglib2.img.basictypeaccess.array.DoubleArray')
    global FloatArray
    FloatArray          = scyjava.jimport('net.imglib2.img.basictypeaccess.array.FloatArray')
    global IntArray
    IntArray            = scyjava.jimport('net.imglib2.img.basictypeaccess.array.IntArray')
    global LongArray
    LongArray           = scyjava.jimport('net.imglib2.img.basictypeaccess.array.LongArray')
    global ShortArray
    ShortArray          = scyjava.jimport('net.imglib2.img.basictypeaccess.array.ShortArray')

    global VolatileByteArray
    VolatileByteArray   = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileByteArray')
    global VolatileCharArray
    VolatileCharArray   = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileCharArray')
    global VolatileDoubleArray
    VolatileDoubleArray = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileDoubleArray')
    global VolatileFloatArray
    VolatileFloatArray  = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileFloatArray')
    global VolatileIntArray
    VolatileIntArray    = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileIntArray')
    global VolatileLongArray
    VolatileLongArray   = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileLongArray')
    global VolatileShortArray
    VolatileShortArray  = scyjava.jimport('net.imglib2.img.basictypeaccess.volatiles.array.VolatileShortArray')

    global ByteUnsafe
    ByteUnsafe          = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
    global CharUnsafe
    CharUnsafe          = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
    global DoubleUnsafe
    DoubleUnsafe        = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
    global FloatUnsafe
    FloatUnsafe         = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
    global IntUnsafe
    IntUnsafe           = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
    global LongUnsafe
    LongUnsafe          = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
    global ShortUnsafe
    ShortUnsafe         = scyjava.jimport('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')

scyjava.when_jvm_starts(_java_setup)


# does not work with strided accesses, currently
def as_array_access(ndarray, volatile=False):
    scyjava.start_jvm()
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

