import imglyb
import numpy as np
from jnius import cast

data       = np.arange(6).reshape((3, 2))
block_size = (2, 2)
img        = imglyb.arraylike_to_img2(data, block_size, volatile=False)
# weirdly, volatile=True produces an error when calling img.cursor()

print(data)
print(img.toString())
cursor = img.cursor()
while cursor.hasNext():
    print(cursor.next().toString())

for d in data.flat:
    print(d)
