import numpy as np
import scyjava

def _java_setup():
    """
    Lazy initialization function for Java-dependent data structures.
    Do not call this directly; use scyjava.start_jvm() instead.
    """

    global NativeType
    NativeType                = scyjava.jimport('net.imglib2.type.NativeType')

    global FloatType
    FloatType                 = scyjava.jimport('net.imglib2.type.numeric.real.FloatType')
    global DoubleType
    DoubleType                = scyjava.jimport('net.imglib2.type.numeric.real.DoubleType')
    global ByteType
    ByteType                  = scyjava.jimport('net.imglib2.type.numeric.integer.ByteType')
    global UnsignedByteType
    UnsignedByteType          = scyjava.jimport('net.imglib2.type.numeric.integer.UnsignedByteType')
    global ShortType
    ShortType                 = scyjava.jimport('net.imglib2.type.numeric.integer.ShortType')
    global UnsignedShortType
    UnsignedShortType         = scyjava.jimport('net.imglib2.type.numeric.integer.UnsignedShortType')
    global IntType
    IntType                   = scyjava.jimport('net.imglib2.type.numeric.integer.IntType')
    global UnsignedIntType
    UnsignedIntType           = scyjava.jimport('net.imglib2.type.numeric.integer.UnsignedIntType')
    global LongType
    LongType                  = scyjava.jimport('net.imglib2.type.numeric.integer.LongType')
    global UnsignedLongType
    UnsignedLongType          = scyjava.jimport('net.imglib2.type.numeric.integer.UnsignedLongType')

    global VolatileFloatType
    VolatileFloatType         = scyjava.jimport('net.imglib2.type.volatiles.VolatileFloatType')
    global VolatileDoubleType
    VolatileDoubleType        = scyjava.jimport('net.imglib2.type.volatiles.VolatileDoubleType')
    global VolatileByteType
    VolatileByteType          = scyjava.jimport('net.imglib2.type.volatiles.VolatileByteType')
    global VolatileUnsignedByteType
    VolatileUnsignedByteType  = scyjava.jimport('net.imglib2.type.volatiles.VolatileUnsignedByteType')
    global VolatileShortType
    VolatileShortType         = scyjava.jimport('net.imglib2.type.volatiles.VolatileShortType')
    global VolatileUnsignedShortType
    VolatileUnsignedShortType = scyjava.jimport('net.imglib2.type.volatiles.VolatileUnsignedShortType')
    global VolatileIntType
    VolatileIntType           = scyjava.jimport('net.imglib2.type.volatiles.VolatileIntType')
    global VolatileUnsignedIntType
    VolatileUnsignedIntType   = scyjava.jimport('net.imglib2.type.volatiles.VolatileUnsignedIntType')
    global VolatileLongType
    VolatileLongType          = scyjava.jimport('net.imglib2.type.volatiles.VolatileLongType')
    global VolatileUnsignedLongType
    VolatileUnsignedLongType  = scyjava.jimport('net.imglib2.type.volatiles.VolatileUnsignedLongType')

scyjava.when_jvm_starts(_java_setup)


def for_np_dtype(dtype, volatile=False):
    scyjava.start_jvm()
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
