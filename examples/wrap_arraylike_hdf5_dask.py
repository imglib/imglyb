import dask.array as da
import dask_image.ndfilters as ndfilters
import h5py
import imglyb
import scyjava
import threading
import time

import logging
logging.basicConfig(level=logging.INFO)

scyjava.config.add_endpoints('sc.fiji:bigdataviewer-vistools:1.0.0-beta-25')
scyjava.start_jvm()

path = '/home/hanslovskyp/Downloads/sample_A_20160501.hdf'


def compute(x):
    return x.compute()


def identity(x):
    return x


BdvFunctions        = imglyb.util.BdvFunctions
BdvOptions          = imglyb.util.BdvOptions
VolatileTypeMatcher = scyjava.jimport('bdv.util.volatiles.VolatileTypeMatcher')
VolatileViews       = scyjava.jimport('bdv.util.volatiles.VolatileViews')

block_size = (30,) * 3
file       = h5py.File(path, 'r')
ds         = file['volumes/raw']
data       = da.from_array(ds, chunks=block_size)
sigma      = (0.1, 1.0, 1.0)
smoothed   = ndfilters.gaussian_filter(data, sigma=sigma)
img1, s1   = imglyb.as_cell_img(ds,       block_size, cache=100, access_type='native', chunk_as_array=identity)
img2, s2   = imglyb.as_cell_img(smoothed, block_size, cache=100, access_type='native', chunk_as_array=compute)
try:
    vimg1  = VolatileViews.wrapAsVolatile(img1)
    vimg2  = VolatileViews.wrapAsVolatile(img2)
except Exception as e:
    print(scyjava.jstacktrace(e))
    raise e

bdv = BdvFunctions.show(vimg1, 'raw')
BdvFunctions.show(vimg2, 'smoothed', BdvOptions.options().addTo(bdv))

System = scyjava.jimport('java.lang.System')

def runUntilBdvDoesNotShow():
    panel = bdv.getBdvHandle().getViewerPanel()
    while panel.isShowing():
        time.sleep(0.3)
        # System.gc()


threading.Thread(target=runUntilBdvDoesNotShow).start()
