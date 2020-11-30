import scyjava

def _java_setup():
    """
    Lazy initialization function for Java-dependent data structures.
    Do not call this directly; use scyjava.start_jvm() instead.
    """
    global BoundedSoftRefLoaderCache
    BoundedSoftRefLoaderCache   = scyjava.jimport('net.imglib2.cache.ref.BoundedSoftRefLoaderCache')
    global GuardedStrongRefLoaderCache
    GuardedStrongRefLoaderCache = scyjava.jimport('net.imglib2.cache.ref.GuardedStrongRefLoaderCache')
    global SoftRefLoaderCache
    SoftRefLoaderCache          = scyjava.jimport('net.imglib2.cache.ref.SoftRefLoaderCache')
    global WeakRefLoaderCache
    WeakRefLoaderCache          = scyjava.jimport('net.imglib2.cache.ref.WeakRefLoaderCache')

scyjava.when_jvm_starts(_java_setup)
