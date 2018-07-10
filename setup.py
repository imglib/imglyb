import os
import glob
from subprocess import call
from distutils.core import setup
from distutils.command.build_py import build_py


execfile('imglyb/version.py')

setup(
    name='imglyb',
    version=__version__,
    author='Philipp Hanslovsky',
    author_email='hanslovskyp@janelia.hhmi.org',
    description='A simple python module to bring together the worlds of numpy (Python) and ImgLib2 (Java).',
    packages=['imglyb'],
    install_requires=['numpy', 'jnius', 'jrun']
)
