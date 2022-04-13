# How to publish to PyPI

1) If present remove build and dist folder

2) Recursively remove all .egg-info files
On powershell you can do this with
```
rm -r *.egg-info
```

3) If not done yet, install build and twine via
```
pip install build twine
```
4) Update the version number in `xmipy/__init__.py`.

5) Re-create the wheels:
```
python -m build
```
6) Check the package files:
```
twine check dist/*
```
7) Re-upload the new files:
```
twine upload dist/*
```
