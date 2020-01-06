from jnius import autoclass

__all__ = (
    'BoundedSoftRefLoaderCache',
    'GuardedStrongRefLoaderCache',
    'SoftRefLoaderCache',
    'WeakRefLoaderCache'
)

BoundedSoftRefLoaderCache   = autoclass('net.imglib2.cache.ref.BoundedSoftRefLoaderCache')
GuardedStrongRefLoaderCache = autoclass('net.imglib2.cache.ref.GuardedStrongRefLoaderCache')
SoftRefLoaderCache          = autoclass('net.imglib2.cache.ref.SoftRefLoaderCache')
WeakRefLoaderCache          = autoclass('net.imglib2.cache.ref.WeakRefLoaderCache')