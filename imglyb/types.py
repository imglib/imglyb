import imglyb
from jnius import autoclass, MetaJavaClass

NativeType = autoclass( 'net.imglib2.type.NativeType' )

FloatType         = autoclass( 'net.imglib2.type.numeric.real.FloatType' )
DoubleType        = autoclass( 'net.imglib2.type.numeric.real.DoubleType' )
ByteType          = autoclass( 'net.imglib2.type.numeric.integer.ByteType' )
UnsignedByteType  = autoclass( 'net.imglib2.type.numeric.integer.UnsignedByteType' )
ShortType         = autoclass( 'net.imglib2.type.numeric.integer.ShortType' )
UnsignedShortType = autoclass( 'net.imglib2.type.numeric.integer.UnsignedShortType' )
IntType           = autoclass( 'net.imglib2.type.numeric.integer.IntType' )
UnsignedIntType   = autoclass( 'net.imglib2.type.numeric.integer.UnsignedIntType' )
LongType          = autoclass( 'net.imglib2.type.numeric.integer.LongType' )
UnsignedLongType  = autoclass( 'net.imglib2.type.numeric.integer.UnsignedLongType' )


if __name__ == "__main__":
	types = {
		(k, v) for k, v in locals().items() if isinstance( v, ( MetaJavaClass, )  ) and not k in 'NativeType'
		}

	for k, v in types:
		print( k, v().toString() )




