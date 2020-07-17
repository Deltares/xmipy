import sys
from setuptools import find_namespace_packages, setup
import os


__version__ = "0.1.1"
__pakname__ = "xmipy"

# edit author dictionary as necessary
author_dict = {
    "Martijn Russcher": "Martijn.Russcher@deltares.nl",
    "Julian Hofer": "Julian.Hofer@deltares.nl",
    "Joseph D. Hughes": "jdhughes@usgs.gov",
}
__author__ = ", ".join(author_dict.keys())
__author_email__ = ", ".join(s for _, s in author_dict.items())


# ensure minimum version of Python is running
if sys.version_info[0:2] < (3, 6):
    raise RuntimeError("Python >= 3.6 is required")


setup(
    name=__pakname__,
    description=f"{__pakname__} is an extension to the bmipy Python package .",
    long_description=f"{__pakname__} is an extension to the bmipy Python package "
    + "for MODFLOW 6 and other codes.",
    author=__author__,
    url="https://github.com/Deltares/xmipy.git",
    license="CC0",
    platforms="Windows, Mac OS-X, Linux",
    install_requires=["bmipy", "numpy"],
    packages=find_namespace_packages(exclude=("tests", "examples")),
    version=__version__,
    classifiers=["Topic :: Scientific/Engineering :: Hydrology"],
)
