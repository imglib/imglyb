from setuptools import setup

version_info={}
with open('imglyb_config.py', 'r') as f:
    exec(f.read(), version_info)
version = version_info['version']

setup(
    python_requires='>=3',
    name='imglyb',
    version=version,
    author='Philipp Hanslovsky, Curtis Rueden, Edward Evans',
    author_email='ctrueden@wisc.edu',
    description='A python module to bring together the worlds of numpy (Python) and ImgLib2 (Java).',
    packages=['imglyb'],
    py_modules=['imglyb_config'],
    install_requires=['numpy', 'jpype1', 'scyjava'],
)
