# Install via the repository

## Clone the repository
```
git clone TODO
```

## Install dependencies
This is only needed if 1) you want to use the avid pyoneer package and 2) for development environments that should be well defined; normal user can skip this step.

either use:
```
pip install -r requirements.txt
```
or
```
make init
```

## Install this package
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




## run tests
either run:
```
python -m unittest discover
```
or
```
make test
```

## optional: download workflow scripts
```
git clone https://phabricator.mitk.org/source/avid-workflows.git AVID-workflows
```

## Have fun

## run scripts
Scripts can be found in subfolder bin. They are declared as entry points
(see setup.py). This means you can call them by calling the entry points
directly in console!