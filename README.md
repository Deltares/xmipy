# xmipy

![Continuous integration](https://github.com/Deltares/xmipy/workflows/Continuous%20integration/badge.svg)
[![codecov](https://codecov.io/gh/Deltares/xmipy/branch/develop/graph/badge.svg)](https://codecov.io/gh/Deltares/xmipy)


`xmipy` is an extension to [bmipy](https://pypi.org/project/bmipy/) including an implementation of the abstract methods.
The extended interface is required to couple certain hydrological kernels, particularly MODFLOW 6. Currently it is a joint development of the USGS and Deltares. The [imod_coupler](https://github.com/Deltares/imod_coupler) uses it, for example, to couple MODFLOW 6 and MetaSWAP.

`xmipy` can be downloaded from [conda-forge](https://anaconda.org/conda-forge/xmipy) or [PyPI](https://pypi.org/project/xmipy/).

# Contributing

In order to develop on `xmipy`, you have to download pixi.
Pixi can be downloaded at [pixi.sh](https://pixi.sh/latest/).

In order to run the test suite, execute:

```bash
pixi run tests
```
