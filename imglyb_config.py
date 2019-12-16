import os

__all__ = ('set_imglib2_imglyb_version', 'get_imglib2_imglyb_version')

__major__   = 0
__minor__   = 3
__patch__   = 6
__tag__     = 'dev0'
__version__ = f'{__major__}.{__minor__}.{__patch__}.{__tag__}'.strip('.')

class _Version(object):

    def major(self):
        return __major__

    def minor(self):
        return __minor__

    def patch(self):
        return __patch__

    def tag(self):
        return __tag__

    def version(self):
        return __version__

    def __str__(self):
        return self.version()

_version = _Version()

version = _version.version()

_default_imglib2_imglyb_version = '0.3.3-SNAPSHOT'
_imglib2_imglyb_version         = os.getenv('IMGLIB2_IMGLYB_VERSION', _default_imglib2_imglyb_version)

def set_imglib2_imglyb_version(version):
    global _imglib2_imglyb_version
    _imglib2_imglyb_version = version

def get_imglib2_imglyb_version():
    global _imglib2_imglyb_version
    return _imglib2_imglyb_version
