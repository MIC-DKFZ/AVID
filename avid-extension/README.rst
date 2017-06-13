AVID extension
========================

Description
-----------
Extension package with additional actions for AVID. The actions of this package where not directly
added to AVID because they have extra dependencies to other python packages (like simpleitk, numpy,...)
After installation of the extension package they can be normally used.

Python requirements
-----------------
Add Python directory and python/scripts to your Windows PATH as otherwise, neither python,
nor avidconfig will be found!

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

Please have in mind that python directory has to be in PATH!

### "normal" install
either use:
```
python setup.py install
```
or
```
make install
```

## Have fun
Add new actions to your avid workflow scripts.