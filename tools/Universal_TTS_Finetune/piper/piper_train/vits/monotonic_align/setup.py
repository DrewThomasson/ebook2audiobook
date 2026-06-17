from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

setup(
    name="monotonic_align",
    ext_modules=cythonize([Extension("core", ["core.pyx"])]),
    include_dirs=[numpy.get_include()],
)
