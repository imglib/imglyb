from functools import lru_cache
import logging
from typing import Any, Callable, Dict

import scyjava
import scyjava.config as sjconf

from .config import get_imglib2_imglyb_version, version as __version__
from .imglib_ndarray import ImgLibReferenceGuard as _ImgLibReferenceGuard
from .ndarray_like_as_img import (
    as_cell_img,
    as_cell_img_with_array_accesses,
    as_cell_img_with_native_accesses,
)
from .util import to_imglib, to_imglib_argb

# Declare public API in a PEP8-compliant way.
# https://peps.python.org/pep-0008/#public-and-internal-interfaces
__all__ = [
    "as_cell_img",
    "as_cell_img_with_array_accesses",
    "as_cell_img_with_native_accesses",
    "to_imglib",
    "to_imglib_argb",
]

__author__ = "ImgLib2 developers"

_logger = logging.getLogger(__name__)

_imglib2_imglyb_version = get_imglib2_imglyb_version()
_IMGLIB2_IMGLYB_ENDPOINT = "net.imglib2:imglib2-imglyb:{}".format(
    _imglib2_imglyb_version
)
sjconf.endpoints.append(_IMGLIB2_IMGLYB_ENDPOINT)


def to_numpy(source):
    scyjava.start_jvm()
    return _ImgLibReferenceGuard(source)


# This is a duplication of work in scyjava.
# It should be removed once https://github.com/scijava/scyjava/issues/40
# has been solved.

# Set of module properties
_CONSTANTS: Dict[str, Callable] = {}


def constant(func: Callable[[], Any], cache=True) -> Callable[[], Any]:
    """
    Turns a function into a property of this module
    Functions decorated with this property must have a
    leading underscore!
    :param func: The function to turn into a property
    """
    if func.__name__[0] != "_":
        raise ValueError(
            f"""Function {func.__name__} must have
            a leading underscore in its name
            to become a module property!"""
        )
    name = func.__name__[1:]
    if cache:
        func = (lru_cache(maxsize=None))(func)
    _CONSTANTS[name] = func
    return func


def __getattr__(name):
    """
    Runs as a fallback when this module does not have an
    attribute.
    :param name: The name of the attribute being searched for.
    """
    if name in _CONSTANTS:
        return _CONSTANTS[name]()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
