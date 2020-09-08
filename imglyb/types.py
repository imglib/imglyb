import numpy as np

import imglyb
import jpype
import jpype.imports

NativeType = jpype.JClass('net.imglib2.type.NativeType')

FloatType                 = jpype.JClass('net.imglib2.type.numeric.real.FloatType')
DoubleType                = jpype.JClass('net.imglib2.type.numeric.real.DoubleType')
ByteType                  = jpype.JClass('net.imglib2.type.numeric.integer.ByteType')
UnsignedByteType          = jpype.JClass('net.imglib2.type.numeric.integer.UnsignedByteType')
ShortType                 = jpype.JClass('net.imglib2.type.numeric.integer.ShortType')
UnsignedShortType         = jpype.JClass('net.imglib2.type.numeric.integer.UnsignedShortType')
IntType                   = jpype.JClass('net.imglib2.type.numeric.integer.IntType')
UnsignedIntType           = jpype.JClass('net.imglib2.type.numeric.integer.UnsignedIntType')
LongType                  = jpype.JClass('net.imglib2.type.numeric.integer.LongType')
UnsignedLongType          = jpype.JClass('net.imglib2.type.numeric.integer.UnsignedLongType')

VolatileFloatType         = jpype.JClass('net.imglib2.type.volatiles.VolatileFloatType')
VolatileDoubleType        = jpype.JClass('net.imglib2.type.volatiles.VolatileDoubleType')
VolatileByteType          = jpype.JClass('net.imglib2.type.volatiles.VolatileByteType')
VolatileUnsignedByteType  = jpype.JClass('net.imglib2.type.volatiles.VolatileUnsignedByteType')
VolatileShortType         = jpype.JClass('net.imglib2.type.volatiles.VolatileShortType')
VolatileUnsignedShortType = jpype.JClass('net.imglib2.type.volatiles.VolatileUnsignedShortType')
VolatileIntType           = jpype.JClass('net.imglib2.type.volatiles.VolatileIntType')
VolatileUnsignedIntType   = jpype.JClass('net.imglib2.type.volatiles.VolatileUnsignedIntType')
VolatileLongType          = jpype.JClass('net.imglib2.type.volatiles.VolatileLongType')
VolatileUnsignedLongType  = jpype.JClass('net.imglib2.type.volatiles.VolatileUnsignedLongType')


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

