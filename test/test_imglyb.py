import pytest
import imglyb
import numpy as np
import scyjava

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