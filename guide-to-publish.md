# How to publish to PyPI

1) If present remove dist folder

2) Recursively remove all .egg-info files
On powershell you can do this with
```
rm -r *.egg-info
```

3) If not done yet, install build and twine via
```
pip install build twine
```

4) Re-create the wheels:
```
python -m build
```

5) Check the package files:
```
twine check dist/*
```

6) Update the version number in `xmipy/__init__.py`.

7) Make a new commit with the updated version number,
and push to remote

8) Make a new github release

9) Re-upload the new files:
```
twine upload dist/*
```
