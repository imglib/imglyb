import dask.array as da
import numpy as np
import scyjava_config
import threading
import time

scyjava_config.add_endpoints('sc.fiji:bigdataviewer-vistools:1.0.0-beta-18')

import imglyb
from jnius import autoclass, JavaException

BdvFunctions        = imglyb.util.BdvFunctions
BdvOptions          = imglyb.util.BdvOptions
VolatileTypeMatcher = autoclass('bdv.util.volatiles.VolatileTypeMatcher')
VolatileViews       = autoclass('bdv.util.volatiles.VolatileViews')

shape      = (150, 100, 125)
block_size = (32,) * 3
data1      = da.random.randint(0, 256, size=shape, chunks=block_size, dtype=np.uint8)
img1, s1   = imglyb.as_cell_img(data1, block_size, access_type='native', chunk_as_array=lambda x: x.compute(), cache=100)
data2      = da.random.randint(0, 256, size=shape, chunks=block_size, dtype=np.uint8)
img2, s2   = imglyb.as_cell_img(data2, block_size, access_type='native', chunk_as_array=lambda x: x.compute(), cache=100)
try:
    vimg1  = VolatileViews.wrapAsVolatile(img1)
    vimg2  = VolatileViews.wrapAsVolatile(img2)
except JavaException as e:
    print(e.classname)
    print(e.innermessage)
    if e.stacktrace:
        for s in e.stacktrace:
            print(s)
    raise e

bdv = BdvFunctions.show(vimg1, 'raw1')
BdvFunctions.show(vimg2, 'raw2', BdvOptions.options().addTo(bdv))

def runUntilBdvDoesNotShow():
    panel = bdv.getBdvHandle().getViewerPanel()
    while panel.isShowing():
        time.sleep(0.3)


threading.Thread(target=runUntilBdvDoesNotShow).start()
