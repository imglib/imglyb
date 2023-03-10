from jpype import JArray, JInt, JLong
import pytest
import imglyb
import numpy as np
import scyjava

from imglyb.imglib_ndarray import NumpyView


class TestImglyb(object):
    def test_arraylike(self, sj_fixture):
        Views = imglyb.util.Views

        shape = (3, 5)
        data = np.arange(np.prod(shape)).reshape(shape)
        block_size = (2, 2)
        img, _ = imglyb.as_cell_img(data, block_size, access_type="native", cache=1)

        cursor = Views.flatIterable(img).cursor()
        expected = 0
        while cursor.hasNext():
            assert expected == cursor.next().get()
            expected += 1

    @pytest.fixture
    def unsafe_img(self):
        UnsafeImgs = scyjava.jimport("net.imglib2.img.unsafe.UnsafeImgs")
        return UnsafeImgs.bytes(2, 3, 4)

    def test_to_numpy_returns_ndarray(self, unsafe_img):
        thing = imglyb.to_numpy(unsafe_img)
        assert isinstance(thing, np.ndarray)

    def test_to_numpy_modification(self, unsafe_img):
        thing = imglyb.to_numpy(unsafe_img)

        fill_value = 2

        thing.fill(fill_value)

        cursor = unsafe_img.cursor()
        while cursor.hasNext():
            assert cursor.next().get() == fill_value

    parameterizations = [
        (True, np.bool_, "net.imglib2.type.logic.NativeBoolType"),
        (-100, np.int8, "net.imglib2.type.numeric.integer.ByteType"),
        (200, np.uint8, "net.imglib2.type.numeric.integer.UnsignedByteType"),
        (-100, np.int16, "net.imglib2.type.numeric.integer.ShortType"),
        (200, np.uint16, "net.imglib2.type.numeric.integer.UnsignedShortType"),
        (-100, np.int32, "net.imglib2.type.numeric.integer.IntType"),
        (200, np.uint32, "net.imglib2.type.numeric.integer.UnsignedIntType"),
        (-100, np.int64, "net.imglib2.type.numeric.integer.LongType"),
        (200, np.uint64, "net.imglib2.type.numeric.integer.UnsignedLongType"),
        (5.5, np.float32, "net.imglib2.type.numeric.real.FloatType"),
        (5.5, np.float64, "net.imglib2.type.numeric.real.DoubleType"),
    ]

    @pytest.mark.parametrize("value, dtype, jtype", parameterizations)
    def test_np_arr_to_RAI_realType(self, value, dtype, jtype):
        """Tests convesion of each supported Imglib2 data type"""
        img = np.array([[value]], dtype=dtype)
        java_img = imglyb.to_imglib(img)
        RAI = scyjava.jimport("net.imglib2.RandomAccessibleInterval")
        assert isinstance(java_img, RAI)
        ra = java_img.randomAccess()
        element = ra.setPositionAndGet(JArray(JInt)(2))
        assert isinstance(element, scyjava.jimport(jtype))
        assert value == element.get()

    parameterizations = [
        (-100, np.int8, "bytes"),
        (200, np.uint8, "unsignedBytes"),
        (-100, np.int16, "shorts"),
        (-100, np.int32, "ints"),
        (200, np.uint32, "unsignedInts"),
        (-100, np.int64, "longs"),
        (200, np.uint64, "unsignedLongs"),
        (5.5, np.float32, "floats"),
        (5.5, np.float64, "doubles"),
    ]

    @pytest.mark.parametrize("value, dtype, func", parameterizations)
    def test_RAI_realType_to_np_arr(self, value, dtype, func):
        """Tests convesion of each supported Imglib2 data type"""
        # Create the test image
        dims = JArray(JLong)(2)
        dims[:] = [1, 1]
        UnsafeImgs = scyjava.jimport("net.imglib2.img.unsafe.UnsafeImgs")
        function = getattr(UnsafeImgs, func)
        assert function
        j_img = function(dims)
        # Set the only value in the image to value
        j_img.randomAccess().setPositionAndGet(JArray(JInt)(2)).set(value)
        # Convert the image to a numpy array
        img = imglyb.to_numpy(j_img)
        assert isinstance(img, np.ndarray)
        assert dtype == img.dtype
        assert value == img[0, 0]


class TestRAIAsNumpyArray:
    @pytest.fixture
    def img(self):
        ArrayImgs = scyjava.jimport("net.imglib2.img.array.ArrayImgs")
        img = ArrayImgs.unsignedBytes(2, 3, 4)
        tmp_val = 1
        cursor = img.cursor()
        while cursor.hasNext():
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
        Intervals = scyjava.jimport("net.imglib2.util.Intervals")
        assert Intervals.numElements(img) == raiAsNumpyArray.size

    @pytest.fixture
    def simple_wrapper(self, simple_img):
        # populate each index with a unique value
        return NumpyView(simple_img)

    def test_all(self, img, raiAsNumpyArray: np.ndarray):
        """Tests any behavior."""
        # simple_img starts out with a one -> Should be true
        assert raiAsNumpyArray.all()
        assert np.all(raiAsNumpyArray)

        # set all values to zero
        cursor = img.cursor()
        while cursor.hasNext():
            cursor.next().set(0)
            # should be false
            assert not raiAsNumpyArray.all()
            assert not np.all(raiAsNumpyArray)

    def test_any(self, img, raiAsNumpyArray: np.ndarray):
        """Tests any behavior."""
        # simple_img starts out with a one -> Should be true
        assert raiAsNumpyArray.any()
        assert np.any(raiAsNumpyArray)

        # set all values to zero
        cursor = img.cursor()
        while cursor.hasNext():
            cursor.next().set(0)

        # now should be false
        assert not raiAsNumpyArray.any()
        assert not np.any(raiAsNumpyArray)
