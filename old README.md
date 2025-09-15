# AVID

Copyright © German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC). Please make sure that your usage of this code is in compliance with the code license.

## Description
AVID is a python framework for the **declarative data-driven processing** of huge amounts of data.
it is especially taillored to deal well with typically bio madical data sets that need processing workflows
with many inputs/outputs, dynamically generated tasks, dynamic linking of input data or collecting of output data.
E.g. I want to have a workflow where I want to register a set of moving images of a patient to a target image of the patient. Only relevant pairs (images of the same patient, allways target with a moving image) should be registered in the right order. Also the number of moving images can change from patient to patient.

AVID is different to other greate data processing frameworks/pipelines (like airflow, luigi, snakemake, nextflow...) or
even custom python scripts as all of those options fall into an imperative pattern when used in AVID core use case scope,
which makes them unecessary complicated to write and maintaine the correct and robust workflow.

AVID is called "data-driven" because the whole control flow and processing is steered by the properties of each data item
(input or output), called Artefacts in AVID.

AVID is called "declarative" because it never explicitly defines a typical workflow DAG. A AVID workflow only defines
which operations, called actions in AVID, can be conducted and which conditions artefacts have to fullfill to be suitable
input data for the different inputs actions provide.
So for each input channel of an action you can declare what artefacts should be selected, how the artefacts should be sorted or splitted in subsets or how the artefacts should be linked to selections of other inputs channels.

It provides a series of actions that can be used to process the data, including `resampling`, `registration`, `radiomics feature calculation` or `python-based actions`. These 
are just examples, a more detailed list can be found [below](#available-actions). 

AVID enables to select, link, sort, and split the data by user defined criteria, e.g. `case_id` and `timepoint`.


## Example

A detailed description of AVID basic concepts and example on how to use it can be found under avid\examples\AVID_introduction.ipynb.

## Quick start

### Installation

#### Python requirements
You must use python 3.x

Add your python directory and python/scripts to your Windows PATH as otherwise, neither python, nor avidconfig will be found!

#### Option 1: Install via pip
The simplest way to install AVID is via PyPi. Simply use the following command to install AVID and all its dependencies:

<span style="color:red">
TODO: This is a temporary link! See: T28581 
</span>

```
pip install --index-url https://test.pypi.org/simple/ avid2
```

#### Option 2: Install via the repository

A detailed description on how to install AVID from the repository, can be found [here](manual_installation.md).


### Configuration

AVID itself is a python framework for data-driven processing. It provides a variety of actions to do so. Many of these actions use external tools, like [MITK Mini Apps]( https://docs.mitk.org/nightly/AdvancedTopicsPage.html#MiniAppExplainPage), which need to be 
configured in order for avid to find and access them.

#### Configure your AVID tools path
To configure AVID to find the needed tools, use
```
avidconfig settings avid.toolspath <your_desired_tools_path>
```
Please have in mind that python/scripts has to be in PATH!

## Get the tools (for the AVID actions)
<span style="color:red">
Is this still up to date?
</span>


<span style="color:grey">
REMARK: This tools feature is currently only supported for Windows systems.
For Linux and MacOS you have to build the tools directly on your machine.
You have two choices:
1. "install" the tools. This means that you will get copies to the tools, but
   it is not connected to any versioning of the version control system the tools
   are stored in.
2. "update" the tools. This will make an svn checkout/update on the central tool
   repository. This is interesting for developers or if you will often update the avid source
   and you want to have an easy possibility to update the tools accordingly.
3. "add" the tools. This will allow to register tools "by hand". This is interesting for
   tools that are currently not centrally stored or are local developments.
</span>

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

###add own/specific tools
use
```
  avidconfig tools add <toolname/actionID> <path to executable>
```
This will registere a new tool with the given toolname/actionID and let the configuration point to the also specified
executable.



# FAQs

