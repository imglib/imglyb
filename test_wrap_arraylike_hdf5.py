import h5py
import scyjava_config
import threading
import time

scyjava_config.add_endpoints('sc.fiji:bigdataviewer-vistools:1.0.0-beta-18')

import imglyb
from jnius import autoclass, cast, JavaException

path = '/home/hanslovskyp/Downloads/sample_A_padded_20160501.hdf'

BdvFunctions        = imglyb.util.BdvFunctions
VolatileTypeMatcher = autoclass('bdv.util.volatiles.VolatileTypeMatcher')
VolatileViews       = autoclass('bdv.util.volatiles.VolatileViews')

file       = h5py.File(path, 'r')
ds         = file['volumes/raw']
block_size = (32,) * 3
img        = imglyb.as_cell_img(ds, block_size, access_type='array', use_volatile_access=True)
try:
    vimg       = VolatileViews.wrapAsVolatile(img)
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