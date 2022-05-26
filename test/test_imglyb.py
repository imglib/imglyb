from jpype import JArray, JInt
import pytest
import imglyb
import numpy as np
import scyjava
from scyjava import config

from imglyb.imglib_ndarray import ImgLibReferenceGuard, NumpyView

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

        fill_value = 2

        thing.fill(fill_value)

        cursor = unsafe_img.cursor()
        while(cursor.hasNext()):
            assert cursor.next().get() == fill_value

class TestRAIAsNumpyArray:
    @pytest.fixture
    def img(self):
        ArrayImgs = scyjava.jimport('net.imglib2.img.array.ArrayImgs')
        img = ArrayImgs.unsignedBytes(2, 3, 4)
        tmp_val = 1
        cursor = img.cursor()
        while(cursor.hasNext()):
            cursor.next().set(tmp_val)
            tmp_val = tmp_val + 1
        return img
    
    @pytest.fixture
    def raiAsNumpyArray(self, img):
        # populate each index with a unique value
        return NumpyView(img)

    def test_get_tuple(self, img, raiAsNumpyArray):
        ra = img.randomAccess()
        arr = JArray(JInt)(3)
        arr[:] = [1, 1, 1]
        j_val = ra.setPositionAndGet(arr).get()
        assert j_val == raiAsNumpyArray[1, 1, 1]
    
    def test_get_int(self, img, raiAsNumpyArray):
        for slice_val in range(len(raiAsNumpyArray)):
            slice = raiAsNumpyArray[slice_val]
            for i in range(slice.shape[0]):
                for j in range(slice.shape[1]):
                    assert slice[i, j] == raiAsNumpyArray[slice_val, i, j]
    

    def test_change_rai(self, img, raiAsNumpyArray):
        """Tests that changes in the img affect the numpy array"""
        ra = img.randomAccess()
        arr = JArray(JInt)(3)
        arr[:] = [1, 1, 1]
        inserted_val = 100
        ra.setPositionAndGet(arr).set(inserted_val)
        assert inserted_val == raiAsNumpyArray[1, 1, 1]

    def test_change_ndarray(self, img, raiAsNumpyArray):
        """Tests that changes in the numpy array affect the img"""
        # Change the value
        inserted_val = 100
        raiAsNumpyArray[1, 1, 1] = inserted_val
        ra = img.randomAccess()
        arr = JArray(JInt)(3)
        arr[:] = [1, 1, 1]
        assert inserted_val == ra.setPositionAndGet(arr).get()

    def test_size(self, img, raiAsNumpyArray: np.ndarray):
        """Tests any behavior."""
        Intervals = scyjava.jimport('net.imglib2.util.Intervals')
        assert Intervals.numElements(img) == raiAsNumpyArray.size

    @pytest.fixture
    def simple_wrapper(self, simple_img):
        # populate each index with a unique value
        return NumpyView(simple_img)

    def test_all(self, img, raiAsNumpyArray: np.ndarray):
        """Tests any behavior."""
        # simple_img starts out with a one -> Should be true
        assert raiAsNumpyArray.all() == True
        assert np.all(raiAsNumpyArray) == True

        # set all values to zero
        cursor = img.cursor()
        while cursor.hasNext():
            cursor.next().set(0)
            # should be false
            assert raiAsNumpyArray.all() == False
            assert np.all(raiAsNumpyArray) == False


    def test_any(self, img, raiAsNumpyArray: np.ndarray):
        """Tests any behavior."""
        # simple_img starts out with a one -> Should be true
        assert raiAsNumpyArray.any() == True
        assert np.any(raiAsNumpyArray) == True

        # set all values to zero
        cursor = img.cursor()
        while cursor.hasNext():
            cursor.next().set(0)

        # now should be false
        assert raiAsNumpyArray.any() == False
        assert np.any(raiAsNumpyArray) == False


        