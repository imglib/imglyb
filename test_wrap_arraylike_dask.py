import dask.array as da
import numpy as np
import scyjava_config
import threading
import time

scyjava_config.add_endpoints('sc.fiji:bigdataviewer-vistools:1.0.0-beta-18')

import imglyb
from jnius import autoclass, JavaException

BdvFunctions        = imglyb.util.BdvFunctions
VolatileTypeMatcher = autoclass('bdv.util.volatiles.VolatileTypeMatcher')
VolatileViews       = autoclass('bdv.util.volatiles.VolatileViews')

shape      = (150, 100, 125)
block_size = (32,) * 3
data       = da.random.randint(0, 256, size=shape, chunks=block_size, dtype=np.uint8)
img        = imglyb.as_cell_img(data, block_size, access_type='array', chunk_as_array=lambda x: x.compute())
try:
    vimg   = VolatileViews.wrapAsVolatile(img)
except JavaException as e:
    print(e.classname)
    print(e.innermessage)
    if e.stacktrace:
        for s in e.stacktrace:
            print(s)
    raise e

bdv = BdvFunctions.show(vimg, 'raw')

def runUntilBdvDoesNotShow():
    panel = bdv.getBdvHandle().getViewerPanel()
    while panel.isShowing():
        time.sleep(0.3)


threading.Thread(target=runUntilBdvDoesNotShow).start()