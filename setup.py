from setuptools import setup

version={}
with open('imglyb/version.py', 'r') as f:
    exec(f.read(), version)

setup(
    python_requires='>=3',
    name='imglyb',
    version=version['__version__'],
    author='Philipp Hanslovsky',
    author_email='hanslovskyp@janelia.hhmi.org',
    description='A simple python module to bring together the worlds of numpy (Python) and ImgLib2 (Java).',
    packages=['imglyb'],
    py_modules=['imglyb_config'],
    install_requires=['numpy', 'pyjnius', 'scyjava'],
)
