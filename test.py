import dask.array

import jnius_config
jnius_config.add_options('-Xmx60g')

import numpy as np

import time

import imglyb
import imglyb.accesses
import imglyb.cell
import imglyb.util

from jnius import cast, JavaException, autoclass

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
# cache  = img.getCache()
# t      = cast('net.imglib2.type.NativeType', img.randomAccess().get().createVariable())
# crInv  = autoclass('bdv.img.cache.CreateInvalidVolatileCell').get(img.getCellGrid(), t, False)
# queue  = autoclass('bdv.util.volatiles.SharedQueue')(1, 1)
# vcache = autoclass('net.imglib2.cache.ref.WeakRefVolatileCache')(cache, queue, crInv)
# ucache = vcache.unchecked()
# cache.unchecked().get(cast('java.lang.Long', 1))
vol    = imglyb.cell.wrap_volatile(img)
# try:
#     vol    = imglyb.cell.wrap_volatile(img)
# except JavaException as e:
#     print(e)
#     print(e.innermessage)
#     print(e.stacktrace)
#
# try:
#     ra = img.randomAccess()
# except Exception as e:
#     print("OGL")
#     print(e)
#     print(e.innermessage)
#     print(e.stacktrace)
#     print("BOGL")
# print(4)

# print(img)

img = PythonHelpers.randomBytes(shape, chunks)

slices = dask.array.core.slices_from_chunks(data.chunks)

def make_access(index):
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
access_generator = imglyb.cell.MakeAccess(make_access)

img = PythonHelpers.imgFromFunc(
    shape,
    chunks,
    access_generator,
    imglyb.types.UnsignedByteType(),
    imglyb.accesses.as_array_access(data[slices[0]].compute(), volatile=True))

# for i, c in enumerate(dask.array.core.slices_from_chunks(data.chunks)):
#     PythonHelpers.getFromCache(img.getCache(), i)



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

