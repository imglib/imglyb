[![Join the chat at https://gitter.im/imglib2-imglyb](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/imglib2-imglyb?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# imglib2-imglyb

`imglyb` aims at connecting two worlds that have been seperated for too long:
 * Python with [numpy](https://github.com/numpy/numpy)
 * Java with [imglib2](https://github.com/imglib/ImgLib2)

`imglib2-imglyb` uses [PyJNIus](https://github.com/kivy/pyjnius) to access `numpy` arrays and expose them to `ImgLib2` through [`imglib2-imglyb`](https://github.com/hanslovsky/imglib2-imglyb).
This means **shared memory** between `numpy` and `ImgLib2`, i.e. any `ImgLib2` algorithm can run on `numpy` arrays without creating copies of the data!
For example, Python users can now make use of the [BigDataViewer](https://github.com/bigdataviewer/bigdataviewer-core) to visualize dense volumetric data.
If you are interested in using `imglyb`, have a look at the [imglyb-examples](https://github.com/hanslovsky/imglyb-examples) repository and extend the examples as needed! In addition to that, [multiple](https://github.com/hanslovsky/imglyb-learnathon) [notebooks](https://nbviewer.jupyter.org/github/imagej/tutorials/blob/master/notebooks/3_-_Advanced_usage/3_-_ImgLyb_-_ImgLib2_-_with_-_scikit-image.ipynb) demonstrate the general use.

**Note**: [`NEP 18`](http://www.numpy.org/neps/nep-0018-array-function-protocol.html) has the potential to improve `numpy` - `imglib` interoperability, especially when converting `imglib2` data structures to `numpy`.

## Installation

`imglyb` is available on conda for Linux, OSX, and Windows:
```bash
conda install -c conda-forge -c hanslovsky imglyb
```
Re-activate the environment after installation to correctly set the environment variables if necessary.
If this does not work for you, please follow the build instructions below.

### Dependencies
If you choose to install imglyb from source (instead of conda) make sure that these dependencies are present at runtime:
 * Python 3
 * Java 8 JDK (JRE is not enough)
 * [Apache Maven](https://maven.apache.org/)
 * [PyJNIus with pyjnius.jar](https://github.com/kivy/pyjnius) with [appropriate environment variables](https://github.com/imglib/imglyb#build-instructions)
 * [jrun](https://github.com/ctrueden/jrun)

### Build

#### Build Dependencies
 * Python 3
 * Java 8
 * [Apache Ant](http://ant.apache.org/)
 * Cython
 * conda (optional, if installing dependencies from conda)
 * git (optional, if installing dependencies from git)
 * GNU Make (Linux/OSX only)

#### Build Instructions

You can install PyJNIus through conda from the `conda-forge` channel:
```bash
conda install -c conda-forge pyjnius
```
This will use OpenJDK from conda-forge. If you prefer to use a different JDK, 
e.g. to use a newer release or for JavaFX projects, you can build PyJNIus from
source on your local machine:

Clone (or download) the PyJNIus repository:
```bash
# get PyJNIus
git clone https://github.com/kivy/pyjnius
cd pyjnius
```
In order to build `pyjnius.jar` and install the pyjnius python package, run on Linux or OSX:
```bash
make # creates build/pyjnius.jar
export JAVA_HOME=/path/to/jdk
make tests # optional
python setup.py install
# Set the appropriate environment variables:
export JAVA_HOME=/path/to/jdk
export PYJNIUS_JAR=/path/to/pyjnius/build/pyjnius.jar
```
On Windows:
```cmd
ant all
python setup.py build_ext --inplace -f
python setup.py install
:: Set the appropriate environment variables:
SET "PYJNIUS_JAR=path\to\pyjnius\pyjnius.jar"
SET "JAVA_HOME=path\to\jdk"
SET "JDK_HOME=%JAVA_HOME%"
```
Note that it can be useful to automate setting up the environment,
either through a script or by adding the appropriate lines to a shell
config file, e.g. `~/.bashrc` or `~/.zshrc` for bash on Linux and OSX.

```bash
cd /path/to/imglyb
pip install .
```
Install jrun through conda
```
conda install -c hanslovsky jrun
```
or install from the latest `python` branch:
```
git clone https://github.com/ctrueden/jrun
pip install jrun
```



## Run

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


