import pytest
import imglyb
import numpy as np
import scyjava
from scyjava import config

from imglyb.imglib_ndarray import ImgLibReferenceGuard

class TestImglyb(object):
    def test_arraylike(self, sj_fixture):
        Views = imglyb.util.Views

        shape      = (3, 5)
        data       = np.arange(np.prod(shape)).reshape(shape)
        block_size = (2, 2)
        img, _     = imglyb.as_cell_img(data, block_size, access_type='native', cache=1)

        cursor = Views.flatIterable(img).cursor()
        expected = 0
        while cursor.hasNext():
            assert expected == cursor.next().get()
            expected += 1
    

    @pytest.fixture
    def unsafe_img(self):
        UnsafeImgs = scyjava.jimport('net.imglib2.img.unsafe.UnsafeImgs')
        return UnsafeImgs.bytes(2, 3, 4)

   
    def test_to_numpy_returns_ndarray(self, unsafe_img):
        thing = imglyb.to_numpy(unsafe_img)
        assert isinstance(thing, np.ndarray)


    def test_to_numpy_modification(self, unsafe_img):
        thing = imglyb.to_numpy(unsafe_img)
        assert isinstance(thing, np.ndarray)

        fill_value = 2

        thing.fill(fill_value)

        cursor = unsafe_img.cursor()
        while(cursor.hasNext()):
            assert cursor.next().get() == fill_value
        