import os
import sys

import pytest

setuptools_file = os.path.join(os.getcwd(), "src", "imglyb", "version.py")


def _imglyb_version():
    """
    Get ImgLyb's version.
    """
    import imglyb

    # It's important that we clear the cache here,
    # so that we can test different behaviors.
    imglyb.___version__.cache_clear()
    # Get the version
    return imglyb.__version__


def test_version_file():
    """Ensures that, ideally, the version from setuptools_scm is used"""
    # Get the version from setuptools_scm
    from setuptools_scm import get_version

    setuptools_version = get_version(write_to="src/imglyb/version.py")
    # Ensure that the version was written to file
    assert os.path.isfile(setuptools_file)
    # Ensure that imglyb.__version__ matches this.
    assert _imglyb_version() == setuptools_version
    # Cleanup - remove file
    os.remove(setuptools_file)
    assert not os.path.isfile(setuptools_file)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python >= 3.8")
def test_version_importlib():
    """
    Ensures that, with imglyb.version.version unavailable,
    importlib.metadata is used next WITH python 3.8+
    """
    # Remove imglyb.version
    sys.modules["imglyb.version"] = None
    # Ensure imglyb.__version__ matches importlib.metadata.version()
    from importlib.metadata import version

    assert _imglyb_version() == version("imglyb")


@pytest.mark.skipif(
    sys.version_info >= (3, 8), reason="importlib used instead for Python 3.8+"
)
def test_version_pkg_resources():
    """
    Ensures that, with imglyb.version.version AND
    importlib.metadata unavailable,
    pkg_resources is used next.
    """
    # Remove imglyb.version
    sys.modules["imglyb.version"] = None
    # Remove importlib.metadata
    sys.modules["importlib.metadata"] = None
    # Ensure imglyb.__version__ matches
    # pkg_resources.get_distribution().version
    from pkg_resources import get_distribution

    assert _imglyb_version() == get_distribution("imglyb").version


def test_version_unvailable():
    """
    Ensures that no version is returned if none of these
    strategies works.
    """
    # Remove imglyb.version
    sys.modules["imglyb.version"] = None
    # Remove importlib.metadata
    sys.modules["importlib.metadata"] = None
    # Remove pkg_resources
    sys.modules["pkg_resources"] = None
    # Ensure imglyb.__version__ is an error message.
    assert (
        _imglyb_version()
        == "Cannot determine version! Ensure pkg_resources is installed!"
    )
