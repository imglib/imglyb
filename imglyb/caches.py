import jpype
import jpype.imports

__all__ = (
    'BoundedSoftRefLoaderCache',
    'GuardedStrongRefLoaderCache',
    'SoftRefLoaderCache',
    'WeakRefLoaderCache'
)

BoundedSoftRefLoaderCache   = jpype.JClass('net.imglib2.cache.ref.BoundedSoftRefLoaderCache')
GuardedStrongRefLoaderCache = jpype.JClass('net.imglib2.cache.ref.GuardedStrongRefLoaderCache')
SoftRefLoaderCache          = jpype.JClass('net.imglib2.cache.ref.SoftRefLoaderCache')
WeakRefLoaderCache          = jpype.JClass('net.imglib2.cache.ref.WeakRefLoaderCache')