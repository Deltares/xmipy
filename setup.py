import sys
from setuptools import setup

from amipy import __version__, __name__, __author__


# ensure minimum version of Python is running
if sys.version_info[0:2] < (3, 6):
    raise RuntimeError('amipy requires Python >= 3.6')


setup(name=__name__,
      description='amipy is a extension to the pybmi Python package .',
      long_description='amipy is a extension to the pybmi Python package ' +
                       'for MODFLOW 6 and other codes.',
      author=__author__,
      author_email='Martijn.Russcher@deltares.nl',
      url='https://github.com/mjr-deltares/modflow6-bmipy.git',
      license='New BSD',
      platforms='Windows, Mac OS-X, Linux',
      install_requires=['bmipy', 'numpy'],
      packages=[__name__],
      include_package_data=True,
      version=__version__,
      classifiers=['Topic :: Scientific/Engineering :: Hydrology'])
