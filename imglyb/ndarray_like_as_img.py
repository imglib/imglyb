from . import accesses
from . import types
from .util import to_imglib
from jnius import JavaException, autoclass, PythonJavaClass, java_method, cast

import math
import numpy as np

PythonHelpers = autoclass('net.imglib2.python.Helpers')

class MakeAccessFunction(PythonJavaClass):
    __javainterfaces__ = ['java/util/function/Function']

    def __init__(self, func):
        super(MakeAccessFunction, self).__init__()
        self.func = func

    @java_method('(Ljava/lang/Object;)Ljava/lang/Object;')
    def apply(self, t):
        return self.func(t)


class MakeAccessBiFunction(PythonJavaClass):
    __javainterfaces__ = ['java/util/function/BiFunction']

    def __init__(self, func):
        super(MakeAccessBiFunction, self).__init__()
        self.func = func

    @java_method('(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;')
    def apply(self, t, u):
        # t: linear index
        # u: size
        # return self.func(t, u)
        # access = self.func(t, u)
        access = None
        print(f'Made access {access}')
        return access


def chunk_index_to_slices(shape, chunk_shape, cell_index):

    grid_dimensions = tuple(
        int(math.ceil(s/sh))
        for s, sh in zip(shape, chunk_shape))[::-1]

    chunk_min = []
    ndims = len(grid_dimensions)

    i = cell_index
    for d in range(ndims):
        c = i % grid_dimensions[d]
        chunk_min.append(c)
        i = (i - c)//grid_dimensions[d]

    chunk_min = chunk_min[::-1]

    slices = tuple(
        slice(c*cs, (c + 1)*cs)
        for c, cs in zip(chunk_min, chunk_shape))

    return slices


def get_chunk(array, chunk_shape, chunk_index):

    slices = chunk_index_to_slices(array.shape, chunk_shape, chunk_index)
    return np.ascontiguousarray(array[slices])


def get_chunk_access(array, chunk_shape, index, volatile=False):

    try:

        chunk = get_chunk(array, chunk_shape, index)
        target = accesses.as_array_access(chunk, volatile=volatile)
        return target

    except JavaException as e:

        print("exception    ", e)
        print("cause        ", e.__cause__)
        print("inner message", e.innermessage)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e

def get_chunk_access_unsafe(array, chunk_shape, index, volatile=False):

    try:

        chunk  = get_chunk(array, chunk_shape, index)
        img    = to_imglib(chunk)
        source = img.getSource()
        return cast('net.imglib2.img.array.ArrayImg', source).update(None)

    except JavaException as e:

        print("exception    ", e)
        print("cause        ", e.__cause__)
        print("inner message", e.innermessage)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e


def as_img(array, chunk_shape, volatile=False):

    access_generator = MakeAccessBiFunction(
        lambda i, s: get_chunk_access(array, chunk_shape, i, volatile=volatile))

    shape = array.shape[::-1]
    chunk_shape = chunk_shape[::-1]

    img = PythonHelpers.imgWithCellLoaderFromFunc(
        shape,
        chunk_shape,
        access_generator,
        types.for_np_dtype(array.dtype, volatile=volatile),
        accesses.as_array_access(
            get_chunk(array, chunk_shape, 0),
            volatile=volatile))  # TODO: is array access really needed here?

    return img

def as_img2(array, chunk_shape, volatile=False):

    access_generator = MakeAccessFunction(
        lambda index: get_chunk_access_unsafe(array, chunk_shape, index, volatile=volatile))

    shape = array.shape[::-1]
    chunk_shape = chunk_shape[::-1]

    img = PythonHelpers.imgFromFunc(
        shape,
        chunk_shape,
        access_generator,
        types.for_np_dtype(array.dtype, volatile=volatile),
        access_generator.apply(0))

    return img
