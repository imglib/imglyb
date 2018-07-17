import numpy as np

import time

import imglyb
import imglyb.accesses
import imglyb.cell
import imglyb.util

from jnius import cast, JavaException

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
img    = imglyb.cell.dask_array_as_cached_cell_img(data, volatile=False)

print(img) 

try:
    imglyb.util.BdvFunctions.show(img, 'WAS DA LOS?')
except JavaException as e:
    print('inner message', e.innermessage)
    print('stack trace  ', e.stacktrace)


while True:
    time.sleep(0.5)
