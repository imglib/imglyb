from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    imglyb_long_description = f.read()

version_info={}
with open('imglyb/config.py', 'r') as f:
    exec(f.read(), version_info)
version = version_info['version']

setup(
    name='imglyb',
    python_requires='>=3',
    packages=find_packages(),
    version=version,
    author='Philipp Hanslovsky, Curtis Rueden, Edward Evans',
    author_email='ctrueden@wisc.edu',
    description='A python module to bring together the worlds of numpy (Python) and ImgLib2 (Java).',
    long_description=imglyb_long_description,
    long_description_content_type='text/markdown',
    license='Simplified BSD License',
    url='https://github.com/imglib/imglyb',
    install_requires=['numpy', 'jpype1', 'scyjava'],
)
