import logging
import sys

import scyjava

from .config import get_imglib2_imglyb_version
from .imglib_ndarray import ImgLibReferenceGuard as _ImgLibReferenceGuard
from .ndarray_like_as_img import \
    as_cell_img, \
    as_cell_img_with_array_accesses, \
    as_cell_img_with_native_accesses
from .util import to_imglib, to_imglib_argb


_logger = logging.getLogger(__name__)

_imglib2_imglyb_version = get_imglib2_imglyb_version()
_IMGLIB2_IMGLYB_ENDPOINT = 'net.imglib2:imglib2-imglyb:{}'.format(_imglib2_imglyb_version)
scyjava.config.add_endpoints(_IMGLIB2_IMGLYB_ENDPOINT)


def to_numpy(source):
    scyjava.start_jvm()
    return _ImgLibReferenceGuard(source)
