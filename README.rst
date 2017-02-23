AVID
========================

Description
-----------
TODO

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

## configure your AVID tools path
use
```
  avidconfig settings avid.toolspath <your_desired_tools_path>
```
Please have in mind that python/scripts has to be in PATH!

## Get the tools (for the AVID actions)
You have two choices:
1. "install" the tools. This means that you will get copies to the tools, but
it is not connected to any versioning of the version control system the tools
are stored in.

2. "update" the tools. This will make an svn checkout/update on the central tool
repository. This is interesting for developers or if you will often update the avid source
and you want to have an easy possibility to update the tools accordingly.

###install all tools specified by your AVID distribution
requirement is an installed SVN (accessible via commandline, e.g. https://tortoisesvn.net.
Be sure to enable command line support in installation) and Visual Studio 2013
redistributable installer for x64 (https://www.microsoft.com/de-de/download/details.aspx?id=40784)

use
```
  avidconfig tools install
```



###update all tools specified by your AVID distribution
use
```
  avidconfig tools update
```

###install or update specific tools
use
```
  avidconfig tools install <toolname1> [<toolname2> [...]]
```
or
```
  avidconfig tools update <toolname1> [<toolname2> [...]]
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

## Have fun

## run scripts
Scripts can be found in subfolder bin. They are declared as entry points
(see setup.py). This means you can call them by calling the entry points
directly in console!