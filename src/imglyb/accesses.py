import numpy as np
import scyjava
from imglyb._java import jc


# does not work with strided accesses, currently
def as_array_access(ndarray, volatile=False):
    scyjava.start_jvm()
    if ndarray.dtype == np.uint8 or ndarray.dtype == np.int8:
        return _as_array_access(
            ndarray,
            jc.ByteUnsafe,
            lambda n: jc.VolatileByteArray(n, True) if volatile else jc.ByteArray(n),
        )
    elif ndarray.dtype == np.uint16 or ndarray.dtype == np.int16:
        return _as_array_access(
            ndarray,
            jc.ShortUnsafe,
            lambda n: jc.VolatileShortArray(n, True) if volatile else jc.ShortArray(n),
        )
    elif ndarray.dtype == np.uint32 or ndarray.dtype == np.int32:
        return _as_array_access(
            ndarray,
            jc.IntUnsafe,
            lambda n: jc.VolatileIntArray(n, True) if volatile else jc.IntArray(n),
        )
    elif ndarray.dtype == np.uint64 or ndarray.dtype == np.int64:
        return _as_array_access(
            ndarray,
            jc.LongUnsafe,
            lambda n: jc.VolatileLongArray(n, True) if volatile else jc.LongArray(n),
        )
    elif ndarray.dtype == np.float32:
        return _as_array_access(
            ndarray,
            jc.FloatUnsafe,
            lambda n: jc.VolatileFloatArray(n, True) if volatile else jc.FloatArray(n),
        )
    elif ndarray.dtype == np.float64:
        return _as_array_access(
            ndarray,
            jc.DoubleUnsafe,
            lambda n: jc.VolatileDoubleArray(n, True)
            if volatile
            else jc.DoubleArray(n),
        )


def _as_array_access(ndarray, src_clazz, tgt_clazz):
    src = src_clazz(ndarray.ctypes.data)
    tgt = tgt_clazz(ndarray.size)
    jc.Accesses.copyAny(src, 0, tgt, 0, ndarray.size)
    return tgt
