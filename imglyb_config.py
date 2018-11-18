import os

__all__ = ('set_imglib2_imglyb_version', 'get_imglib2_imglyb_version')

version = '0.3.4'

_default_imglib2_imglyb_version = '0.3.0'
_imglib2_imglyb_version         = os.getenv('IMGLIB2_IMGLYB_VERSION', _default_imglib2_imglyb_version)

def set_imglib2_imglyb_version(version):
    global _imglib2_imglyb_version
    _imglib2_imglyb_version = version

def get_imglib2_imglyb_version():
    global _imglib2_imglyb_version
    return _imglib2_imglyb_version
