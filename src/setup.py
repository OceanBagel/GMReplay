from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import setup
from setuptools.extension import Extension

from constants import VERSION_NUMBER

setup(
    name="GMReplay",
    version=VERSION_NUMBER,
    ext_modules=cythonize(
        [
            Extension("*", ["./*.py"])
        ],
        build_dir="./build",
        compiler_directives={
            "language_level": "3",
            "always_allow_keywords": True,
        },
    ),
    cmdclass=dict(build_ext=build_ext),
)
