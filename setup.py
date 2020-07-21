import sys
from setuptools import find_namespace_packages, setup
import codecs
import os.path

# edit author dictionary as necessary
author_dict = {
    "Martijn Russcher": "Martijn.Russcher@deltares.nl",
    "Julian Hofer": "Julian.Hofer@deltares.nl",
    "Joseph D. Hughes": "jdhughes@usgs.gov",
}
__author__ = ", ".join(author_dict.keys())
__author_email__ = ", ".join(s for _, s in author_dict.items())


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


long_description = read("README.md")


# ensure minimum version of Python is running
if sys.version_info[0:2] < (3, 6):
    raise RuntimeError("Python >= 3.6 is required")


setup(
    name="xmipy",
    description="xmipy is an extension to the bmipy Python package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__author_email__,
    url="https://github.com/Deltares/xmipy.git",
    license="CC0",
    platforms="Windows, Mac OS-X, Linux",
    install_requires=["bmipy", "numpy"],
    packages=find_namespace_packages(exclude=("tests", "examples")),
    version=get_version("xmipy/__init__.py"),
    classifiers=["Topic :: Scientific/Engineering :: Hydrology"],
)
