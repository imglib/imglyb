import numpy as np

import imglyb
from jnius import autoclass, MetaJavaClass

NativeType = autoclass('net.imglib2.type.NativeType')

FloatType                 = autoclass('net.imglib2.type.numeric.real.FloatType')
DoubleType                = autoclass('net.imglib2.type.numeric.real.DoubleType')
ByteType                  = autoclass('net.imglib2.type.numeric.integer.ByteType')
UnsignedByteType          = autoclass('net.imglib2.type.numeric.integer.UnsignedByteType')
ShortType                 = autoclass('net.imglib2.type.numeric.integer.ShortType')
UnsignedShortType         = autoclass('net.imglib2.type.numeric.integer.UnsignedShortType')
IntType                   = autoclass('net.imglib2.type.numeric.integer.IntType')
UnsignedIntType           = autoclass('net.imglib2.type.numeric.integer.UnsignedIntType')
LongType                  = autoclass('net.imglib2.type.numeric.integer.LongType')
UnsignedLongType          = autoclass('net.imglib2.type.numeric.integer.UnsignedLongType')

VolatileFloatType         = autoclass('net.imglib2.type.volatiles.VolatileFloatType')
VolatileDoubleType        = autoclass('net.imglib2.type.volatiles.VolatileDoubleType')
VolatileByteType          = autoclass('net.imglib2.type.volatiles.VolatileByteType')
VolatileUnsignedByteType  = autoclass('net.imglib2.type.volatiles.VolatileUnsignedByteType')
VolatileShortType         = autoclass('net.imglib2.type.volatiles.VolatileShortType')
VolatileUnsignedShortType = autoclass('net.imglib2.type.volatiles.VolatileUnsignedShortType')
VolatileIntType           = autoclass('net.imglib2.type.volatiles.VolatileIntType')
VolatileUnsignedIntType   = autoclass('net.imglib2.type.volatiles.VolatileUnsignedIntType')
VolatileLongType          = autoclass('net.imglib2.type.volatiles.VolatileLongType')
VolatileUnsignedLongType  = autoclass('net.imglib2.type.volatiles.VolatileUnsignedLongType')


def for_np_dtype(dtype, volatile=False):
    if dtype == np.uint8:
        return VolatileUnsignedByteType() if volatile else UnsignedByteType()
    if dtype == np.int8:
        return VolatileByteType() if volatile else ByteType()

    if dtype == np.uint16:
        return VolatileUnsignedShortType() if volatile else UnsignedShortType()
    if dtype == np.int16:
        return VolatileShortType() if volatile else ShortType()

    if dtype == np.uint32:
        return VolatileUnsignedIntType() if volatile else UnsignedIntType()
    if dtype == np.int32:
        return VolatileIntType() if volatile else IntType()

    if dtype == np.uint64:
        return VolatileUnsignedLongType() if volatile else UnsignedLongType()
    if dtype == np.int64:
        return VolatileLongType() if volatile else LongType()

    if dtype == np.float32:
        return VolatileFloatType() if volatile else FloatType()
    if dtype == np.float64:
        return VolatileDoubleType() if volatile else DoubleType()

