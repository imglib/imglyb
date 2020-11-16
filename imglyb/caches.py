from jpype import JClass

__all__ = (
    'BoundedSoftRefLoaderCache',
    'GuardedStrongRefLoaderCache',
    'SoftRefLoaderCache',
    'WeakRefLoaderCache'
)

BoundedSoftRefLoaderCache   = JClass('net.imglib2.cache.ref.BoundedSoftRefLoaderCache')
GuardedStrongRefLoaderCache = JClass('net.imglib2.cache.ref.GuardedStrongRefLoaderCache')
SoftRefLoaderCache          = JClass('net.imglib2.cache.ref.SoftRefLoaderCache')
WeakRefLoaderCache          = JClass('net.imglib2.cache.ref.WeakRefLoaderCache')
