[![Join the chat at https://gitter.im/imglib2-imglyb](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/imglib2-imglyb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# imglib2-imglyb

`imglyb` aims at connecting two worlds that have been seperated for too long:
 * Python with [numpy](https://github.com/numpy/numpy)
 * Java with [imglib2](https://github.com/imglib/ImgLib2)

`imglib2-imglyb` uses [PyJNIus](https://github.com/kivy/pyjnius) to access `numpy` arrays and expose them to `ImgLib2` through [`imglib2-imglyb`](https://github.com/hanslovsky/imglib2-imglyb).
This means **shared memory** between `numpy` and `ImgLib2`, i.e. any `ImgLib2` algorithm can run on `numpy` arrays without creating copies of the data!
For example, Python users can now make use of the [BigDataViewer](https://github.com/bigdataviewer/bigdataviewer-core) to visualize dense volumetric data.
If you are interested in using `imglyb`, have a look at the [imglyb-examples](https://github.com/hanslovsky/imglyb-examples) repository and extend the examples as needed! In addition to that, [multiple](https://github.com/hanslovsky/imglyb-learnathon) [notebooks](https://nbviewer.jupyter.org/github/imagej/tutorials/blob/master/notebooks/3_-_Advanced_usage/3_-_ImgLyb_-_ImgLib2_-_with_-_scikit-image.ipynb) demonstrate the general use.



## Installation

`imglyb` is available on conda for Linux, OSX, and Windows:
```bash
conda install -c hanslovsky imglyb
```
Re-activate the environment after installation to correctly set the environment variables if necessary.
If this does not work for you, please follow the build instructions below.

### Requirements
OpenJDK 8, Maven, and Ant are available through anaconda if necessary.
 * Python 3
 * Java 8
 * [Apache Maven](https://maven.apache.org/)
 * [Apache Ant](http://ant.apache.org/)
 * [imglib2-unsafe](https://github.com/imglib/imglib2-unsafe)
 * pyjnius.jar (see instructions below)
 * Cython

### Build
Clone (or download) the PyJNIus repository:
```bash
# get PyJNIus
git clone https://github.com/kivy/pyjnius
cd pyjnius
```
In order to build `pyjnius.jar` and install the pyjnius python package, run on Linux or OSX:
```bash
make # creates build/pyjnius.jar
export JAVA_HOME=/path/to/jdk  # optional
make tests # optional
python setup.py install
```
On Windows:
```bash
ant all
python setup.py build_ext --inplace -f
python setup.py install
```

```bash
cd /path/to/imglyb
python setup.py install
# alternatively
pip install .
```
Install jrun through conda
```
conda install -c hanslovsky jrun
```
or install from the latest `python` branch:
```
git clone https://github.com/hanslovsky/jrun
git checkout python
pip install .
```



## Run

### Requirements
All requirements will be met if you install from my conda channel `hanslovsky`.
 * PyJNIus
 * Java 8
 * Maven
 * numpy
 * jrun

### Run
If you do not use conda you need to set your environment before using `imglib2-imglyb`:
```bash
export JAVA_HOME=/path/to/JAVA_HOME # not necessary if using conda
export PYJNIUS_JAR=/path/to/pyjnius/build/pyjnius.jar # not necessary if using conda
```
Note that, in your python files, the line
```python
import imglyb
```
needs to come before any of
```python
from imglyb import util
import jnius
from jnius import *
```
It is best to follow and extend the [imglyb-examples](https://github.com/hanslovsky/imglyb-examples) according to your needs.

## Known Issues
### AWT through PyJNIus on OSX

AWT, PyJNIus, and Cocoa do not get along perfectly. In general, the Cocoa event loop needs to be started before the JVM is loaded. (Thanks to @tpietzsch for figuring this out!) This requires some OS X specific code, written using `PyObjC`, to properly start up and shut down the Cocoa application and start the Java/Python code within it.

The `OSXAWTwrapper.py` script included in the `imglyb` library provides an example of Cocoa code and can be used to run the `imglyb-examples`. Two packages from `PyObjC` are required for this wrapper (`pyobjc-core` and `pyobjc-framework-cocoa`), and they should be installed with `imglib2-imglyb` on OS X. 

When running the wrapper, one can either provide the name of the target module (as if using `python -m`) or the full path to the target script. So using the module name, the command to run the "butterfly" script in `imglyb-examples` looks like this: `python imglyb/OSXAWTwrapper.py imglyb-examples.butterfly`

Running `OSXAWTwrapper.py` via `python -m` does not work at this time.


