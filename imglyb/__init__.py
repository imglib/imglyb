from __future__ import print_function

import logging
import sys

_logger = logging.getLogger(__name__)

__all__ = ('to_imglib', 'to_imglib_argb', 'to_numpy')

def _init_jvm_options():
    import imglyb_config
    import jnius_config
    import scyjava_config

    imglib2_imglyb_version = imglyb_config.get_imglib2_imglyb_version()

    if jnius_config.vm_running:
        _logger.warning('JVM is already running, will not add relevant endpoints to classpath -- '
                        'required classes might not be on classpath. '
                        'In case of failure, try importing imglyb before scyjava or jnius')
        return jnius_config

    IMGLIB2_IMGLYB_ENDPOINT = 'net.imglib:imglib2-imglyb:{}'.format(imglib2_imglyb_version)
    RELEVANT_MAVEN_REPOS    = {
        'imagej.public' : 'https://maven.imagej.net/content/groups/public',
        'saalfeldlab'   : 'https://saalfeldlab.github.io/maven'
    }
    for _, repo in scyjava_config.get_repositories():
        if repo == RELEVANT_MAVEN_REPOS['imagej.public']:
            del RELEVANT_MAVEN_REPOS['imagej.public']
        if repo == RELEVANT_MAVEN_REPOS['saalfeldlab']:
            del RELEVANT_MAVEN_REPOS['saalfeldlab']
    scyjava_config.add_repositories(RELEVANT_MAVEN_REPOS)
    scyjava_config.add_endpoints(IMGLIB2_IMGLYB_ENDPOINT)

    import scyjava

    return jnius_config, scyjava


config, _ = _init_jvm_options()

if sys.version_info[0] < 3:
    print("Using python < 3. Upgrade to python 3 recommended")
    from imglib_ndarray import ImgLibReferenceGuard as _ImgLibReferenceGuard
    from util import \
        to_imglib, \
        to_imglib_argb
else:
    from .imglib_ndarray import ImgLibReferenceGuard as _ImgLibReferenceGuard
    from .util import \
        to_imglib, \
        to_imglib_argb


def to_numpy(source):
    return _ImgLibReferenceGuard(source)
