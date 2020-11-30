import logging

import numpy as np
import scyjava

from jpype import JImplements, JOverride, JLong, JArray

_logger = logging.getLogger(__name__)

__all__ = (
    'to_imglib',
    'to_imglib_argb',
    'options2D'
)

def _java_setup():
    """
    Lazy initialization function for Java-dependent data structures.
    Do not call this directly; use scyjava.start_jvm() instead.
    """

    # java
    global Random
    Random = scyjava.jimport('java.util.Random')

    # imglib
    global Helpers
    Helpers                            = scyjava.jimport('net.imglib2.python.Helpers')
    global NumpyToImgLibConversions
    NumpyToImgLibConversions           = scyjava.jimport('net.imglib2.python.NumpyToImgLibConversions')
    global NumpyToImgLibConversionsWithStride
    NumpyToImgLibConversionsWithStride = scyjava.jimport('net.imglib2.python.NumpyToImgLibConversionsWithStride')
    global Views
    Views                              = scyjava.jimport('net.imglib2.view.Views')

    # bigdataviewer
    global BdvFunctions
    BdvFunctions = scyjava.jimport('bdv.util.BdvFunctions')
    global BdvOptions
    BdvOptions   = scyjava.jimport('bdv.util.BdvOptions')

    # Guard
    global ReferenceGuardingRandomAccessibleInterval
    ReferenceGuardingRandomAccessibleInterval = scyjava.jimport('net.imglib2.python.ReferenceGuardingRandomAccessibleInterval')

    global numpy_dtype_to_conversion_method
    numpy_dtype_to_conversion_method = {
        np.dtype('complex64')  : NumpyToImgLibConversions.toComplexFloat,
        np.dtype('complex128') : NumpyToImgLibConversions.toComplexDouble,
        np.dtype('float32')    : NumpyToImgLibConversions.toFloat,
        np.dtype('float64')    : NumpyToImgLibConversions.toDouble,
        np.dtype('int8')       : NumpyToImgLibConversions.toByte,
        np.dtype('int16')      : NumpyToImgLibConversions.toShort,
        np.dtype('int32')      : NumpyToImgLibConversions.toInt,
        np.dtype('int64')      : NumpyToImgLibConversions.toLong,
        np.dtype('uint8')      : NumpyToImgLibConversions.toUnsignedByte,
        np.dtype('uint16')     : NumpyToImgLibConversions.toUnsignedShort,
        np.dtype('uint32')     : NumpyToImgLibConversions.toUnsignedInt,
        np.dtype('uint64')     : NumpyToImgLibConversions.toUnsignedLong
    }

    global numpy_dtype_to_conversion_with_stride_method
    numpy_dtype_to_conversion_with_stride_method = {
        np.dtype('complex64')  : NumpyToImgLibConversionsWithStride.toComplexFloat,
        np.dtype('complex128') : NumpyToImgLibConversionsWithStride.toComplexDouble,
        np.dtype('float32')    : NumpyToImgLibConversionsWithStride.toFloat,
        np.dtype('float64')    : NumpyToImgLibConversionsWithStride.toDouble,
        np.dtype('int8')       : NumpyToImgLibConversionsWithStride.toByte,
        np.dtype('int16')      : NumpyToImgLibConversionsWithStride.toShort,
        np.dtype('int32')      : NumpyToImgLibConversionsWithStride.toInt,
        np.dtype('int64')      : NumpyToImgLibConversionsWithStride.toLong,
        np.dtype('uint8')      : NumpyToImgLibConversionsWithStride.toUnsignedByte,
        np.dtype('uint16')     : NumpyToImgLibConversionsWithStride.toUnsignedShort,
        np.dtype('uint32')     : NumpyToImgLibConversionsWithStride.toUnsignedInt,
        np.dtype('uint64')     : NumpyToImgLibConversionsWithStride.toUnsignedLong
    }

    global ReferenceGuard
    @JImplements('net.imglib2.python.ReferenceGuardingRandomAccessibleInterval$ReferenceHolder')
    class ReferenceGuard():

        def __init__(self, *args, **kwargs):
            self.args = args

    global GenericMouseMotionListener
    @JImplements('java.awt.event.MouseMotionListener')
    class GenericMouseMotionListener():

        def __init__(self, mouse_dragged=lambda e: None, mouse_moved=lambda e: None):
            self.mouse_dragged = mouse_dragged
            self.mouse_moved = mouse_moved

        @JOverride
        def mouseDragged(self, e):
            self.mouse_dragged(e)

        @JOverride
        def mouseMoved(self, e):
            self.mouse_moved(e)

    global GenericOverlayRenderer
    @JImplements('net.imglib2.ui.OverlayRenderer')
    class GenericOverlayRenderer():

        def __init__(self, draw_overlays=lambda g: None, set_canvas_size=lambda w, h: None):
            self.draw_overlays = draw_overlays
            self.set_canvas_size = set_canvas_size

        @JOverride
        def drawOverlays(self, g):
            self.draw_overlays(g)

        @JOverride
        def setCanvasSize(self, width, height):
            self.set_canvas_size(width, height)

    global RunnableFromFunc
    @JImplements('java.lang.Runnable')
    class RunnableFromFunc():

        def __init__(self, func):
            self.func = func

        @JOverride
        def run(self):
            _logger.debug('Running function %s', self.func)
            self.func()

scyjava.when_jvm_starts(_java_setup)


def _get_address(source):
    return source.ctypes.data


# how to use type hints for python < 3.5?
def to_imglib(source):
    scyjava.start_jvm()
    return ReferenceGuardingRandomAccessibleInterval(_to_imglib(source), ReferenceGuard(source))


# how to use type hints for python < 3.5?
def _to_imglib(source):
    address = _get_address(source)
    long_address = JLong(address)
    long_arr_source = JArray(JLong)(source.shape[::-1])

    if not source.dtype in numpy_dtype_to_conversion_method:
        raise NotImplementedError("Cannot convert dtype to ImgLib2 type yet: {}".format(source.dtype))
    elif source.flags['CARRAY']:
        return numpy_dtype_to_conversion_method[source.dtype](long_address, *long_arr_source)
    else:
        stride = np.array(source.strides[::-1]) / source.itemsize
        long_arr_stride = JArray(JLong)(stride)
        return numpy_dtype_to_conversion_with_stride_method[source.dtype](long_address, long_arr_stride, long_arr_source)


def to_imglib_argb(source):
    scyjava.start_jvm()
    return ReferenceGuardingRandomAccessibleInterval(_to_imglib_argb(source), ReferenceGuard(source))


def _to_imglib_argb(source):
    address = _get_address(source)
    long_address = JLong(address)
    long_arr_source = JArray(JLong)(source.shape[::-1])

    if not (source.dtype == np.dtype('int32') or source.dtype == np.dtype('uint32')):
        raise NotImplementedError("source.dtype must be int32 or uint32")
    if source.flags['CARRAY']:
        return NumpyToImgLibConversions.toARGB(long_address, *long_arr_source)
    else:
        stride = np.array(source.strides[::-1]) / source.itemsize
        long_arr_stride = JArray(JLong)(stride)
        return NumpyToImgLibConversionsWithStride.toARGB(long_address, long_arr_stride, long_arr_source)


def options2D():
    scyjava.start_jvm()
    return BdvOptions.options().is2D()
