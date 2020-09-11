import numpy as np
import imglyb

from jpype import JClass

NativeType = JClass('net.imglib2.type.NativeType')

FloatType                 = JClass('net.imglib2.type.numeric.real.FloatType')
DoubleType                = JClass('net.imglib2.type.numeric.real.DoubleType')
ByteType                  = JClass('net.imglib2.type.numeric.integer.ByteType')
UnsignedByteType          = JClass('net.imglib2.type.numeric.integer.UnsignedByteType')
ShortType                 = JClass('net.imglib2.type.numeric.integer.ShortType')
UnsignedShortType         = JClass('net.imglib2.type.numeric.integer.UnsignedShortType')
IntType                   = JClass('net.imglib2.type.numeric.integer.IntType')
UnsignedIntType           = JClass('net.imglib2.type.numeric.integer.UnsignedIntType')
LongType                  = JClass('net.imglib2.type.numeric.integer.LongType')
UnsignedLongType          = JClass('net.imglib2.type.numeric.integer.UnsignedLongType')

VolatileFloatType         = JClass('net.imglib2.type.volatiles.VolatileFloatType')
VolatileDoubleType        = JClass('net.imglib2.type.volatiles.VolatileDoubleType')
VolatileByteType          = JClass('net.imglib2.type.volatiles.VolatileByteType')
VolatileUnsignedByteType  = JClass('net.imglib2.type.volatiles.VolatileUnsignedByteType')
VolatileShortType         = JClass('net.imglib2.type.volatiles.VolatileShortType')
VolatileUnsignedShortType = JClass('net.imglib2.type.volatiles.VolatileUnsignedShortType')
VolatileIntType           = JClass('net.imglib2.type.volatiles.VolatileIntType')
VolatileUnsignedIntType   = JClass('net.imglib2.type.volatiles.VolatileUnsignedIntType')
VolatileLongType          = JClass('net.imglib2.type.volatiles.VolatileLongType')
VolatileUnsignedLongType  = JClass('net.imglib2.type.volatiles.VolatileUnsignedLongType')


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

