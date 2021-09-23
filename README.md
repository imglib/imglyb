# imglyb

`imglyb` aims at connecting two worlds that have been seperated for too long:
 * Python with [numpy](https://github.com/numpy/numpy)
 * Java with [ImgLib2](https://github.com/imglib/imglib2)

`imglyb` uses [jpype](http://jpype.org) to access `numpy` arrays and expose
them to `ImgLib2` through
[`imglib2-imglyb`](https://github.com/imglib/imglib2-imglyb).
This means **shared memory** between `numpy` and `ImgLib2`, i.e. any `ImgLib2`
algorithm can run on `numpy` arrays without creating copies of the data!
For example, Python users can now make use of the
[BigDataViewer extension](https://github.com/imglib/imglyb-bdv) to visualize dense volumetric
data.

If you are interested in using `imglyb`, have a look at the `examples` folder
and extend the examples as needed!

**Note**:
[`NEP 18`](https://numpy.org/neps/nep-0018-array-function-protocol.html) has
the potential to improve `numpy` - `imglib` interoperability, especially when
converting `imglib2` data structures to `numpy`.

## Installation

### Prerequisites

`imglyb` has been tested on Linux, macOS, and Windows.

The following tools are required:

 * Python 3
 * Java 8 or 11 JDK (JRE is not enough)
 * [Apache Maven](https://maven.apache.org/)

If you use [conda](https://conda.io/), these will be installed for you.

### Installing with conda

```shell
conda install -c conda-forge imglyb
```

### Installing with pip

First, install the prerequisites above. Then run:

```shell
pip install imglyb
```

It is recommended to do this from inside a virtualenv or conda environment,
rather than system-wide.

### Installing from source

First, install the prerequisites above. Then run:

```shell
git clone git://github.com/imglib/imglyb
cd imglyb
pip install -e .
```

It is recommended to do this from inside a virtualenv or conda environment,
rather than system-wide.

## Usage

It is suggested to follow and extend the examples in the `examples` folder
according to your needs.

Or, for a higher-level way to use `imglyb`, check out
[pyimagej](https://github.com/imagej/pyimagej).

## Known Issues

### AWT on macOS

AWT and Cocoa do not get along perfectly. In general, the Cocoa event loop
needs to be started before the JVM is loaded. (Thanks to @tpietzsch for
figuring this out!) This requires some macOS specific code, written using
`PyObjC`, to properly start up and shut down the Cocoa application and start
the Java/Python code within it.

The `OSXAWTwrapper.py` script included in the `imglyb` library provides an
example of Cocoa code and can be used to run the `imglyb` examples. Two
packages from `PyObjC` are required for this wrapper (`pyobjc-core` and
`pyobjc-framework-cocoa`), and they should be installed with `imglyb`
on macOS.

When running the wrapper, one can either provide the name of the target module
(as if using `python -m`) or the full path to the target script. So using the
module name, the command to run the "butterfly" script in `imglyb-examples`
looks like this:
```shell
python imglyb/OSXAWTwrapper.py imglyb-examples.butterfly
```
Running `OSXAWTwrapper.py` via `python -m` does not work at this time.
