import ctypes

import numpy as np
import jpype
import scyjava

from imglyb import util


def _java_setup():
    """
    Lazy initialization function for Java-dependent data structures.
    Do not call this directly; use scyjava.start_jvm() instead.
    """
    global Intervals
    Intervals = scyjava.jimport("net.imglib2.util.Intervals")


scyjava.when_jvm_starts(_java_setup)

dtype_selector = {
    "FloatType": np.dtype("float32"),
    "FloatLongAccessType": np.dtype("float32"),
    "DoubleType": np.dtype("float64"),
    "DoubleLongAccessType": np.dtype("float64"),
    "ByteType": np.dtype("int8"),
    "ByteLongAccessType": np.dtype("int8"),
    "UnsignedByteType": np.dtype("uint8"),
    "UnsignedByteLongAccessType": np.dtype("uint8"),
    "ShortType": np.dtype("int16"),
    "ShortLongAccessType": np.dtype("int16"),
    "UnsignedShortType": np.dtype("uint16"),
    "UnisgnedShortLongAccessType": np.dtype("uint16"),
    "IntType": np.dtype("int32"),
    "IntLongAccessType": np.dtype("int32"),
    "UnsignedIntType": np.dtype("uint32"),
    "UnsignedIntLongAccessType": np.dtype("uint32"),
    "LongType": np.dtype("int64"),
    "LongLongAccessType": np.dtype("int64"),
    "UnsignedLongType": np.dtype("uint64"),
    "UnsignedLongLongAccessType": np.dtype("uint64"),
}

ctype_conversions_imglib = {
    "FloatType": ctypes.c_float,
    "FloatLongAccessType": ctypes.c_float,
    "DoubleType": ctypes.c_double,
    "DoubleLongAccessType": ctypes.c_double,
    "ByteType": ctypes.c_int8,
    "ByteLongAccessType": ctypes.c_int8,
    "UnsignedByteType": ctypes.c_uint8,
    "UnsignedByteLongAccessType": ctypes.c_uint8,
    "ShortType": ctypes.c_int16,
    "ShortLongAccessType": ctypes.c_int16,
    "UnsignedShortType": ctypes.c_uint16,
    "UnsignedShortLongAccessType": ctypes.c_uint16,
    "IntType": ctypes.c_int32,
    "IntLongAccessType": ctypes.c_int32,
    "UnsignedIntType": ctypes.c_uint32,
    "UnsignedIntLongAccessType": ctypes.c_uint32,
    "LongType": ctypes.c_int64,
    "LongLongAccessType": ctypes.c_int64,
    "UnsignedLongType": ctypes.c_uint64,
    "UnsignedLongLongAccessType": ctypes.c_uint64,
}


def get_address(rai):
    scyjava.start_jvm()
    class_name = scyjava.to_python(util.Helpers.classNameSimple(rai))
    class_name_full = scyjava.to_python(util.Helpers.className(rai))
    if class_name in ("ArrayImg", "UnsafeImg"):
        img_class = scyjava.jimport(class_name_full)
        access = jpype.JObject(rai, img_class).update(None)
        access_type = scyjava.to_python(util.Helpers.className(access))

        if "basictypelongaccess.unsafe" in access_type:
            return jpype.JObject(access, access_type).getAddress()
        else:
            raise ValueError(f"Excpected unsafe access but got {access_type}")

    else:
        raise ValueError(
            "Excpected ArrayImg or UnsafeImg but got {}".format(class_name)
        )


class ImgLibReferenceGuard(np.ndarray):
    def __new__(cls, rai):
        # Access the address of the rai's data
        access = rai.randomAccess()
        rai.min(access)
        imglib_type = util.Helpers.classNameSimple(access.get())
        address = get_address(rai)

        # Set python properties
        shape = tuple(Intervals.dimensionsAsLongArray(rai))[::-1]
        dtype = dtype_selector[imglib_type]

        # Create a ctypes pointer to the data
        pointer = ctypes.cast(
            address, ctypes.POINTER(ctype_conversions_imglib[imglib_type])
        )

        # Create a new numpy array
        obj = np.ndarray.__new__(
            cls,
            buffer=np.ctypeslib.as_array(pointer, shape=shape),
            shape=shape,
            dtype=dtype,
        )
        obj.setflags(write=True)
        # Maintain a reference to the java object
        obj.rai = rai
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.rai = obj.rai


HANDLED_FUNCTIONS = {}


class NumpyView(np.ndarray):
    def __new__(cls, rai):
        access = rai.randomAccess()
        rai.min(access)
        imglib_type = util.Helpers.classNameSimple(access.get())
        dtype = dtype_selector[imglib_type]

        shape = tuple(Intervals.dimensionsAsLongArray(rai))[::-1]
        obj = super().__new__(NumpyView, shape=shape, dtype=dtype)

        # Maintain a reference to the java object
        obj.rai = rai
        return obj

    def __init__(self, rai):
        self.rai = rai

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.rai = obj.rai

    def __array_function__(self, func, types, args, kwargs):
        if func not in HANDLED_FUNCTIONS:
            return NotImplemented
            # Note: this allows subclasses that don"t override
            # __array_function__ to handle DiagonalArray objects.
        if not all(issubclass(t, self.__class__) for t in types):
            return NotImplemented
        return HANDLED_FUNCTIONS[func](*args, **kwargs)

    def __getitem__(self, key):
        if isinstance(key, slice):
            print("Got a slice")
        elif isinstance(key, int):
            Views = scyjava.jimport("net.imglib2.view.Views")
            return NumpyView(
                Views.hyperSlice(self.rai, self.rai.numDimensions() - 1, key)
            )
        elif isinstance(key, tuple):
            ra = self.rai.randomAccess()
            for i in range(len(key)):
                ra.setPosition(key[i] % self.shape[i], len(key) - 1 - i)
            val = ra.get().get()
            if val != 0:
                print(val)
            return ra.get().get()
        else:
            raise ValueError(f"Cannot parse key {key}")

    def __setitem__(self, key, value):
        # print(f"key: {key}")
        # return 0
        if isinstance(key, slice):
            print("Got a slice")
        elif isinstance(key, int):
            print("Got an int")
        elif isinstance(key, tuple):
            ra = self.rai.randomAccess()
            for i in range(len(key)):
                ra.setPosition(key[i] % self.shape[i], len(key) - 1 - i)
            ra.get().set(value)
        else:
            raise ValueError(f"Cannot parse key {key}")

    def all(self):
        return np.all(self)

    def any(self):
        return np.any(self)


def implements(np_function):
    "Register an __array_function__ implementation for DiagonalArray objects."

    def decorator(func):
        HANDLED_FUNCTIONS[np_function] = func
        return func

    return decorator


@implements(np.all)
def np_all(arr: NumpyView):
    for index in np.ndindex(*arr.shape):
        if not arr[index]:
            return False
    return True


@implements(np.any)
def np_any(arr: NumpyView):
    for index in np.ndindex(*arr.shape):
        if arr[index]:
            return True
    return False


if __name__ == "__main__":
    ArrayImgs = scyjava.jimport("net.imglib2.img.array.ArrayImgs")
    UnsafeUtil = scyjava.jimport(
        "net.imglib2.img.basictypelongaccess.unsafe.UnsafeUtil"
    )
    Arrays = scyjava.jimport("java.util.Arrays")
    OwningFloatUnsafe = scyjava.jimport(
        "net.imglib2.img.basictypelongaccess.unsafe.owning.OwningFloatUnsafe"
    )
    Fraction = scyjava.jimport("net.imglib2.util.Fraction")
    LongStream = scyjava.jimport("java.util.stream.LongStream")

    shape = (2, 3, 4)
    n_elements = int(np.prod(shape))
    data_store = OwningFloatUnsafe(n_elements)
    dim_array = LongStream.of(*shape).toArray()
    print(Arrays.toString(dim_array))
    rai = util.Helpers.toArrayImg(
        jpype.JObject(util.Helpers.className(data_store), data_store), dim_array
    )
    # rai = ArrayImgs.floats( *shape )
    c = rai.cursor()
    count = 23
    while c.hasNext():
        c.next().setReal(count)
        count += 1
    print(util.Helpers.className(rai.randomAccess().get()))
    print(util.Helpers.classNameSimple(rai.randomAccess().get()))
    arr = ImgLibReferenceGuard(rai)
    print(arr, arr.mean())
    c = rai.cursor()
    c.fwd()
    c.next().setReal(0)
    print(arr, arr.mean())
