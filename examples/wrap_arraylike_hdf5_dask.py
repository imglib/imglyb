import dask.array as da
import dask_image.ndfilters as ndfilters
import h5py
import scyjava_config
import threading
import time

scyjava_config.add_endpoints('sc.fiji:bigdataviewer-vistools:1.0.0-beta-18')

import imglyb
from jnius import autoclass, cast, JavaException

path = '/home/hanslovskyp/Downloads/sample_A_20160501.hdf'


def compute(x):
    return x.compute()


def identity(x):
    return x


BdvFunctions        = imglyb.util.BdvFunctions
BdvOptions          = imglyb.util.BdvOptions
VolatileTypeMatcher = autoclass('bdv.util.volatiles.VolatileTypeMatcher')
VolatileViews       = autoclass('bdv.util.volatiles.VolatileViews')

block_size = (30,) * 3
file       = h5py.File(path, 'r')
ds         = file['volumes/raw']
data       = da.from_array(ds, chunks=block_size)
sigma      = (0.1, 1.0, 1.0)
smoothed   = ndfilters.gaussian_filter(data, sigma=sigma)
img1, s1   = imglyb.as_cell_img(ds,       block_size, access_type='array', chunk_as_array=identity)
img2, s2   = imglyb.as_cell_img(smoothed, block_size, access_type='native', chunk_as_array=compute)
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

bdv = BdvFunctions.show(vimg1, 'raw')
BdvFunctions.show(vimg2, 'smoothed', BdvOptions.options().addTo(bdv))

System = autoclass('java.lang.System')

def runUntilBdvDoesNotShow():
    # while True:
    #     time.sleep(0.3)
    panel = bdv.getBdvHandle().getViewerPanel()
    while panel.isShowing():
        time.sleep(0.3)
        img1.getCache().invalidateAll()
        img2.getCache().invalidateAll()
        System.gc()
    print(s1, s2)


threading.Thread(target=runUntilBdvDoesNotShow).start()