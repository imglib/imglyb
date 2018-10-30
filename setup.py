import os
import glob
from subprocess import call
from distutils.core import setup
from distutils.command.build_py import build_py

version={}
with open('imglyb/version.py', 'r') as f:
    exec(f.read(), version)

setup(
    name='imglyb',
    version=version['__version__'],
    author='Philipp Hanslovsky',
    author_email='hanslovskyp@janelia.hhmi.org',
    description='A simple python module to bring together the worlds of numpy (Python) and ImgLib2 (Java).',
    packages=['imglyb'],
    py_modules=['imglyb_config'],
    install_requires=['numpy', 'pyjnius', 'jrun']
)
