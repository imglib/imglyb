"""
Internal utility functions for working with Java resources.
"""

from scyjava import JavaClasses


class JavaClassResources(JavaClasses):
    """Utility class used to make importing frequently-used "Access"
    java classes easier and more readable.
    """

    @JavaClasses.java_import
    def Accesses(self):
        return "net.imglib2.img.basictypeaccess.Accesses"

    @JavaClasses.java_import
    def ByteArray(self):
        return "net.imglib2.img.basictypeaccess.array.ByteArray"

    @JavaClasses.java_import
    def CharArray(self):
        return "net.imglib2.img.basictypeaccess.array.CharArray"

    @JavaClasses.java_import
    def DoubleArray(self):
        return "net.imglib2.img.basictypeaccess.array.DoubleArray"

    @JavaClasses.java_import
    def FloatArray(self):
        return "net.imglib2.img.basictypeaccess.array.FloatArray"

    @JavaClasses.java_import
    def IntArray(self):
        return "net.imglib2.img.basictypeaccess.array.IntArray"

    @JavaClasses.java_import
    def LongArray(self):
        return "net.imglib2.img.basictypeaccess.array.LongArray"

    @JavaClasses.java_import
    def ShortArray(self):
        return "net.imglib2.img.basictypeaccess.array.ShortArray"

    @JavaClasses.java_import
    def VolatileByteArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileByteArray"

    @JavaClasses.java_import
    def VolatileCharArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileCharArray"

    @JavaClasses.java_import
    def VolatileDoubleArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileDoubleArray"

    @JavaClasses.java_import
    def VolatileFloatArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileFloatArray"

    @JavaClasses.java_import
    def VolatileIntArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileIntArray"

    @JavaClasses.java_import
    def VolatileLongArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileLongArray"

    @JavaClasses.java_import
    def VolatileShortArray(self):
        return "net.imglib2.img.basictypeaccess.volatiles.array.VolatileShortArray"

    @JavaClasses.java_import
    def ByteUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.ByteUnsafe"

    @JavaClasses.java_import
    def CharUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.CharUnsafe"

    @JavaClasses.java_import
    def DoubleUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.DoubleUnsafe"

    @JavaClasses.java_import
    def FloatUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.FloatUnsafe"

    @JavaClasses.java_import
    def IntUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.IntUnsafe"

    @JavaClasses.java_import
    def LongUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.LongUnsafe"

    @JavaClasses.java_import
    def ShortUnsafe(self):
        return "net.imglib2.img.basictypelongaccess.unsafe.ShortUnsafe"


jc = JavaClassResources()
