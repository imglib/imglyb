from functools import lru_cache
import logging
import sys

import scyjava
import scyjava.config as sjconf
import imglyb.version

from .config import get_imglib2_imglyb_version
from .imglib_ndarray import ImgLibReferenceGuard as _ImgLibReferenceGuard
from .ndarray_like_as_img import (
    as_cell_img,
    as_cell_img_with_array_accesses,
    as_cell_img_with_native_accesses,
)
from .util import to_imglib, to_imglib_argb


_logger = logging.getLogger(__name__)

_imglib2_imglyb_version = get_imglib2_imglyb_version()
_IMGLIB2_IMGLYB_ENDPOINT = "net.imglib2:imglib2-imglyb:{}".format(
    _imglib2_imglyb_version
)
sjconf.endpoints.append(_IMGLIB2_IMGLYB_ENDPOINT)


def to_numpy(source):
    scyjava.start_jvm()
    return _ImgLibReferenceGuard(source)


def module_property(func):
    """Decorator to turn module functions into properties.
    Function names must be prefixed with an underscore."""
    module = sys.modules[func.__module__]

    def base_getattr(name):
        raise AttributeError(f"module '{module.__name__}' has no attribute '{name}'")

    old_getattr = getattr(module, "__getattr__", base_getattr)

    def new_getattr(name):
        if f"_{name}" == func.__name__:
            return func()
        else:
            return old_getattr(name)

    module.__getattr__ = new_getattr
    return func


@module_property
def ___version__():
    from pkg_resources import get_distribution

    return get_distribution("imglyb").version
