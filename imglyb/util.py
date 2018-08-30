from __future__ import division

import ctypes

from collections import defaultdict

from jnius import autoclass, PythonJavaClass, java_method

import numpy as np

import sys

__all__ = (
    'to_imglib',
    'to_imglib_argb',
    'options2D'
)

# java
Random = autoclass('java.util.Random')

# imglib
Helpers                            = autoclass('net.imglib2.python.Helpers')
NumpyToImgLibConversions           = autoclass('net.imglib2.python.NumpyToImgLibConversions')
NumpyToImgLibConversionsWithStride = autoclass('net.imglib2.python.NumpyToImgLibConversionsWithStride')
Views                              = autoclass('net.imglib2.view.Views')

# bigdataviewer
BdvFunctions = autoclass('bdv.util.BdvFunctions')
BdvOptions   = autoclass('bdv.util.BdvOptions')

# Guard
ReferenceGuardingRandomAccessibleInterval = autoclass('net/imglib2/python/ReferenceGuardingRandomAccessibleInterval')

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


def _get_address(source):
    return source.ctypes.data


class ReferenceGuard(PythonJavaClass):
    __javainterfaces__ = ['net/imglib2/python/ReferenceGuardingRandomAccessibleInterval$ReferenceHolder']

    def __init__(self, *args, **kwargs):
        super(ReferenceGuard, self).__init__()
        self.args = args


# how to use type hints for python < 3.5?
def to_imglib(source):
    return ReferenceGuardingRandomAccessibleInterval(_to_imglib(source), ReferenceGuard(source))


# how to use type hints for python < 3.5?
def _to_imglib(source):
    address = _get_address(source)
    if not source.dtype in numpy_dtype_to_conversion_method:
        raise NotImplementedError("Cannot convert dtype to ImgLib2 type yet: {}".format(source.dtype))
    elif source.flags['CARRAY']:
        return numpy_dtype_to_conversion_method[source.dtype](address, *source.shape[::-1])
    else:
        stride = np.array(source.strides[::-1]) / source.itemsize
        return numpy_dtype_to_conversion_with_stride_method[source.dtype](address, tuple(stride), source.shape[::-1])


def to_imglib_argb(source):
    return ReferenceGuardingRandomAccessibleInterval(_to_imglib_argb(source), ReferenceGuard(source))


def _to_imglib_argb(source):
    address = _get_address(source)
    if not (source.dtype == np.dtype('int32') or source.dtype == np.dtype('uint32')):
        raise NotImplementedError("source.dtype must be int32 or uint32")
    if source.flags['CARRAY']:
        return NumpyToImgLibConversions.toARGB(address, *source.shape[::-1])
    else:
        stride = np.array(source.strides[::-1]) / source.itemsize
        return NumpyToImgLibConversionsWithStride.toARGB(address, tuple(stride), source.shape[::-1])


def options2D():
    return BdvOptions.options().is2D()


class GenericOverlayRenderer(PythonJavaClass):
    __javainterfaces__ = ['net/imglib2/ui/OverlayRenderer']

    def __init__(self, draw_overlays=lambda g: None, set_canvas_size=lambda w, h: None):
        super(GenericOverlayRenderer, self).__init__()
        self.draw_overlays = draw_overlays
        self.set_canvas_size = set_canvas_size

    @java_method('(Ljava/awt/Graphics;)V')
    def drawOverlays(self, g):
        self.draw_overlays(g)

    @java_method('(II)V')
    def setCanvasSize(self, width, height):
        self.set_canvas_size(width, height)


class GenericMouseMotionListener(PythonJavaClass):
    __javainterfaces__ = ['java/awt/event/MouseMotionListener']

    def __init__(self, mouse_dragged=lambda e: None, mouse_moved=lambda e: None):
        super(GenericMouseMotionListener, self).__init__()
        self.mouse_dragged = mouse_dragged
        self.mouse_moved = mouse_moved

    @java_method('(Ljava/awt/event/MouseEvent;)V')
    def mouseDragged(self, e):
        self.mouse_dragged(e)

    @java_method('(Ljava/awt/event/MouseEvent;)V')
    def mouseMoved(self, e):
        self.mouse_moved(e)
