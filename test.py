import dask.array

import jnius_config
jnius_config.add_options('-Xmx60g')

import numpy as np

import time

import imglyb
import imglyb.accesses
import imglyb.cell
import imglyb.util

from jnius import cast, JavaException, autoclass, PythonJavaClass, java_method

PythonHelpers               = autoclass('net.imglib2.python.Helpers')

for dtype in (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64, np.float32, np.float64):
    arr = np.arange(10, dtype=dtype)
    acc = imglyb.accesses.as_array_access(arr, volatile=True)
    print(arr)
    print(np.array(acc.getCurrentStorageArray()))

print()

for dtype in (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64, np.float32, np.float64):
    arr = np.arange(10, dtype=dtype)
    acc = imglyb.accesses.as_array_access(arr, volatile=False)
    print(arr)
    print(np.array(acc.getCurrentStorageArray()))


import dask.array
shape  = (100, 200, 300)
chunks = (64, 64, 64)
# to see that it irregular chunks fail, uncomment next line:
# chunks = (64, 64, (64,36,100,100))
data   = dask.array.from_array(np.random.randint(255, size=shape, dtype=np.uint8), chunks=chunks).rechunk(chunks)
img    = imglyb.cell.dask_array_as_cached_cell_img(data, volatile_access=True)
slices = dask.array.core.slices_from_chunks(data.chunks)


# alternative way generate cell img:
# def make_access(index):
#     try:
#         chunk    = data[slices[index]].compute()
#         refGuard = imglyb.util.ReferenceGuard(chunk)
#         address  = chunk.ctypes.data
#         target   = imglyb.accesses.as_array_access(chunk, volatile=True)
#         return target
#     except JavaException as e:
#         print('exception    ', e)
#         print('cause        ', e.__cause__ )
#         print('inner message', e.innermessage)
#         if e.stacktrace:
#             for line in e.stacktrace:
#                 print(line)

#         raise e
# access_generator = imglyb.cell.MakeAccess(make_access)
# img              = PythonHelpers.imgFromFunc(
#     shape,
#     chunks,
#     access_generator,
#     imglyb.types.UnsignedByteType(),
#     imglyb.accesses.as_array_access(data[slices[0]].compute(), volatile=True))

class MakeAccessBiFunction(PythonJavaClass):
    __javainterfaces__ = ['java/util/function/BiFunction']

    def __init__(self, func):
        super(MakeAccessBiFunction, self).__init__()
        self.func = func

    @java_method('(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;')
    def apply(self, t, u):
        return self.func(t, u)

def make_access(index, size):
    try:
        chunk    = data[slices[index]].compute()
        refGuard = imglyb.util.ReferenceGuard(chunk)
        address  = chunk.ctypes.data
        target   = imglyb.accesses.as_array_access(chunk, volatile=True)
        return target
    except JavaException as e:
        print('exception    ', e)
        print('cause        ', e.__cause__ )
        print('inner message', e.innermessage)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e

access_generator = MakeAccessBiFunction(make_access)
img              = PythonHelpers.imgWithCellLoaderFromFunc(
    shape,
    chunks,
    access_generator,
    imglyb.types.UnsignedByteType(),
    imglyb.accesses.as_array_access(data[slices[0]].compute(), volatile=True))




try:
    # pass
    imglyb.util.BdvFunctions.show(img, 'WAS DA LOS?')
except JavaException as e:
    print('exception    ', e)
    print('cause        ', e.__cause__ )
    print('inner message', e.innermessage)
    if e.stacktrace:
        for line in e.stacktrace:
            print(line)


while True:
    time.sleep(0.5)

