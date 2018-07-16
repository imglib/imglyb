import numpy as np

import imglyb
from jnius import autoclass


Accesses     = autoclass('tmp.net.imglib2.img.basictypeaccess.Accesses')

ByteArray    = autoclass('net.imglib2.img.basictypeaccess.array.ByteArray')
CharArray    = autoclass('net.imglib2.img.basictypeaccess.array.CharArray')
DoubleArray  = autoclass('net.imglib2.img.basictypeaccess.array.DoubleArray')
FloatArray   = autoclass('net.imglib2.img.basictypeaccess.array.FloatArray')
IntArray     = autoclass('net.imglib2.img.basictypeaccess.array.IntArray')
LongArray    = autoclass('net.imglib2.img.basictypeaccess.array.LongArray')
ShortArray   = autoclass('net.imglib2.img.basictypeaccess.array.ShortArray')

ByteUnsafe   = autoclass('net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe')
CharUnsafe   = autoclass('net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe')
DoubleUnsafe = autoclass('net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe')
FloatUnsafe  = autoclass('net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe')
IntUnsafe    = autoclass('net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe')
LongUnsafe   = autoclass('net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe')
ShortUnsafe  = autoclass('net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe')

# does not work with strided accesses, currently
def as_array_access(ndarray):
    if ndarray.dtype == np.uint8 or ndarray.dtype == np.int8:
        return _as_array_access(ndarray, ByteUnsafe, ByteArray)
    elif ndarray.dtype == np.uint16 or ndarray.dtype == np.int16:
        return _as_array_access(ndarray, ShortUnsafe, ShortArray)
    elif ndarray.dtype == np.uint32 or ndarray.dtype == np.int32:
        return _as_array_access(ndarray, IntUnsafe, IntArray)
    elif ndarray.dtype == np.uint64 or ndarray.dtype == np.int64:
        return _as_array_access(ndarray, LongUnsafe, LongArray)
    elif ndarray.dtype == np.float32:
        return _as_array_access(ndarray, FloatUnsafe, FloatArray)
    elif ndarray.dtype == np.float64:
        return _as_array_access(ndarray, DoubleUnsafe, DoubleArray)

def _as_array_access(ndarray, src_clazz, tgt_clazz):
    src = src_clazz(ndarray.ctypes.data)
    tgt = tgt_clazz(ndarray.size)
    Accesses.copyAny(src, 0, tgt, 0, ndarray.size)
    return tgt

