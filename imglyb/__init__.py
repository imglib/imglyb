from __future__ import print_function

from .version import __version__

import os

import sys

__all__ = ('to_imglib', 'to_imglib_argb', 'to_numpy')

__imglib2_imglyb_version__ = os.getenv('IMGLIB2_IMGLYB_VERSION', '0.3.0')

__additional_endpoints_variable__ = "ADDITIONAL_ENDPOINTS"


def _init_jvm_options():
    import imglyb_config

    import jnius_config

    import jrun.jrun

    import os

    IMGLIB2_IMGLYB_ENDPOINT = 'net.imglib:imglib2-imglyb:{}'.format(__imglib2_imglyb_version__)
    PYJNIUS_JAR_STR         = 'PYJNIUS_JAR'
    IMGLYB_JAR_CACHE_DIR    = os.path.join(os.getenv('HOME'), '.imglyb-jars')
    LOCAL_MAVEN_REPO        = os.getenv('M2_REPO', os.path.join(os.getenv('HOME'), '.m2', 'repository'))
    RELEVANT_MAVEN_REPOS    = {
        'imagej.public' : 'https://maven.imagej.net/content/groups/public',
        'saalfeldlab'   : 'https://saalfeldlab.github.io/maven'
    }
    imglyb_config.add_repositories(RELEVANT_MAVEN_REPOS)

    if PYJNIUS_JAR_STR not in globals():
        try:
            PYJNIUS_JAR = os.environ[PYJNIUS_JAR_STR]
        except KeyError as e:
            print("Path to pyjnius.jar not defined! Use environment variable {} to define it.".format(PYJNIUS_JAR_STR))
            raise e

    if 'classpath' in globals():
        jnius_config.add_classpath(classpath)

    CLASSPATH_STR = 'CLASSPATH'
    if CLASSPATH_STR in os.environ:
        for path in os.environ[CLASSPATH_STR].split(jnius_config.split_char):
            jnius_config.add_classpath(path)

    jnius_config.add_classpath(PYJNIUS_JAR)
    additional_endpoints = os.getenv(__additional_endpoints_variable__, None)
    if (additional_endpoints):
        imglyb_config.add_endpoints(additional_endpoints)
    primary_endpoint, workspace = jrun.jrun.resolve_dependencies(
        '+'.join([IMGLIB2_IMGLYB_ENDPOINT] + imglyb_config.get_endpoints()),
        cache_dir=IMGLYB_JAR_CACHE_DIR,
        m2_repo=LOCAL_MAVEN_REPO,
        repositories=imglyb_config.get_repositories(),
        verbose=2
    )
    jnius_config.add_classpath(os.path.join(workspace, '*'))

    JVM_OPTIONS_STR = 'JVM_OPTIONS'

    if JVM_OPTIONS_STR in os.environ:
        jnius_config.add_options(*os.environ[JVM_OPTIONS_STR].split(' '))

    return jnius_config


config = _init_jvm_options()

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
