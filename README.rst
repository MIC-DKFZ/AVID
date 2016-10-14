AVID
========================

Description
-----------
TODO

## install dependencies
either use:
```
pip install -r requirements.txt
```
or
```
make init
```

## install this package
You have two choices:
1. install a development version. This means that if you make
changes to the packages code you make will affect the code you write which is
based on this package.
2. "normal" install. This will install the current version.

After you installed your package, it can be imported in your via import sample
where ever you are.

### install development version:
either use:
```
python setup.py develop
```
or
```
make install_develop
```

### "normal" install
either use:
```
python setup.py install
```
or
```
make install
```

## run tests
either run:
```
python -m unittest discover
```
or
```
make test
```

## execute tutorial
In your console, navigate to the tutorials subfolder and start ipython notebook.


## run scripts
Scripts can be found in subfolder bin. They are declared as entry points
(see setup.py). This means you can call them by calling the entry points
directly in console!