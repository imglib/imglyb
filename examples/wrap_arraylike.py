import scyjava.config
scyjava.config.add_endpoints('sc.fiji:bigdataviewer-vistools:1.0.0-beta-18')

import imglyb
import numpy as np
from jnius import cast

Views = imglyb.util.Views

shape      = (3, 5)
data       = np.arange(np.prod(shape)).reshape(shape)
block_size = (2, 2)
img, _     = imglyb.as_cell_img(data, block_size, access_type='native', cache=1)

print(data)
print(img.toString())
cursor = Views.flatIterable(img).cursor()

print('Cell Img')
while cursor.hasNext():
    print(cursor.next().toString())

print()
print('ndarray')
for d in data.flat:
    print(d)
print(data)

print()
print('cells')
cursor = cast('net.imglib2.IterableInterval', img.getCells()).cursor()
cellIdx = 0
while cursor.hasNext():
    cell = cursor.next()
    access = cell.getData()
    print(f'Cell index: {cellIdx} {access}')
    size = cell.size()
    for idx in range(0, size):
        print(access.getValue(idx))
    cellIdx += 1
    break
