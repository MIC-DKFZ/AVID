# AVID - Automated processing of Versatile Image Data

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-DKFZ-green.svg)](LICENSE)

**AVID** is a Python framework for **declarative, data-driven processing** of large-scale image datasets, particularly designed for biomedical image analysis workflows.

## 🎯 What makes AVID special?

Unlike traditional workflow engines that require explicit DAG definitions, AVID uses a **declarative data-driven approach** where the workflow is automatically determined by the properties of your data itself. This makes it incredibly flexible and scalable - whether you're processing a single case or thousands of patients across multiple timepoints and modalities.

###  Key Features

- **🔄 Data-driven**: Workflow automatically scales based on your data structure
- **📝 Declarative**: Define what you want, not how to do it
- **🔗 Smart linking**: Automatically pairs related data (same patient, timepoint, etc.)
- **⚡ Batch processing**: Efficiently handles large cohorts
- **🔧 Extensible**: Easy to add new processing steps
- **📊 Reproducible**: Full tracking of processing steps and metadata
- **🚀 Runtime flexible**: Allows running locally, in containers, or on HPC clusters (eg. LSF, SLURM) with just configuration changes 

### 🤝 Use Cases

AVID excels in scenarios involving:
- **Multi-modal imaging studies** (CT, MR, PET, etc.)
- **Longitudinal analysis** (multiple timepoints per patient)
- **Large cohort studies** (hundreds to thousands of patients)
- **Complex processing pipelines** with many interdependent steps
- **Reproducible research** requiring full processing provenance
- **Flexible deployment**: Need to run the same workflow in different runtime environments (e.g. locally during development and on HPC clusters for production)

For more thoughts on when to use AVID and when other options might be better suited please see the section below: [When to Choose AVID vs Other Workflow Tools](#-when-to-choose-avid-vs-other-workflow-tools)


## 🚀 Quick Start

### Installation

```bash
pip install avid
```
or, if you are working with a console/terminal that supports nice rich output, we advice to install AVID with the packgage rich.
```bash
pip install avid[rich]
```

### Basic Example

```python
import avid.common.workflow as workflow
from avid.actions.pythonAction import PythonUnaryBatchAction
from avid.selectors import ValiditySelector

# Initialize session with your data
session = workflow.initSession(
    bootstrapArtefacts="path/to/your/data.avid",
    sessionPath="output/session.avid",
    name="my_analysis"
)

# Define a simple processing function
def process_image(outputs, inputs, **kwargs):
    # Your image processing logic here
    # The inputs that should be used is indicated by "inputs"
    # The location where the results should be stored are indicated by "outputs"
    pass

# Apply to all valid data
with session:
    PythonUnaryBatchAction(
        inputSelector=ValiditySelector(),
        generateCallable=process_image,
        actionTag="processed",
        defaultoutputextension="nii.gz"
    ).do()
```

## 🏗️ Core Concepts

### Data
This is the dataset which is being processed in the workflow. It contains the "raw" input data to the workflow and the output data of each processing step. The data can be located for example in a data folder or a database such as a PACS system. Each data item within the dataset has a URL pointing to where it is located.

### Artefact
Your data is represented as **artefacts** - metadata containers that describe each piece of data (images, results, etc.) with properties like patient ID, timepoint, modality, and file location.
The artefacts of a session can be written out in an xml-file. An exemplary artefact looks like this:
```xml
<avid:artefact>
    <avid:property key="case">pat1</avid:property>
    <avid:property key="timePoint">TP1</avid:property>
    <avid:property key="actionTag">CT</avid:property>
    <avid:property key="type">result</avid:property>
    <avid:property key="format">itk</avid:property>
    <avid:property key="url">../data/img/pat1_TP1_CT.txt</avid:property>
    <avid:property key="invalid">False</avid:property>
    <avid:property key="id">bbe232b8-5740-11ec-85a6-e9d058c65a83</avid:property>
    <avid:property key="timestamp">1638869608.3330662</avid:property>
</avid:artefact>
```

### Session
The session is a set of artefact that should be processed by a workflow. It can be seen as a "blackboard" which contains all the relevant metadata about the *data* in the form of *artefacts*. It can be read from and written to by the *actions*. The user can directly feed information about the initial input data to the session in the form of an xml file. It is also possible to gain insights into the current session by writing out the artefacts as items of an xml-file.


### Datacrawler Script
**Datacrawler scripts** are one of two types of scripts that AVID users create. Datacrawler scripts define how to discover and index your raw data. They crawl through your data folders, extract metadata from file (content, names or locations), transform it into artefacts, and create the initial session file with bootstrap artefacts:

```python
# datacrawler.py - discovers your data and creates bootstrap session
# Crawls data folder, extracts patient ID, timepoint, modality from filenames
# Creates bootstrap.avid with all discovered data items and their properties
%run datacrawler.py /path/to/data/ output/bootstrap.avid
```


### Action
**Actions** are processing steps that transform your data. AVID provides many built-in actions for common image processing tasks, and you can easily create custom ones.


### Selector
**Selectors** choose which data to process based on properties:
Data is not explicitly handed to actions. Instead, *selectors* are used to specify which artefacts should be used as input to an action. This way, instead of using all currently available artefacts from the session we can declare only a selection.
A selector selects artefacts based on properties. All available built-in selectors are located in the folder `.\avid\selectors`.

```python
# Process only MR images (which are indicated by the action tag 'MR'.
selector = ActionTagSelector('MR')
```


### Linker
**Linkers** intelligently pair related data. This is needed as a actions can also be given more than a single input, meaning they don't have to work on individual artefacts, but can also work on pairs of artefacts (or even more).
For example we could wish to perform a registration of MR and CT images, which takes both images as input. We can use a selector to select the desired images, but there is a problem. How do we clarify which artefacts belong together in a pair? Theoretically, each MR image could be paired with each CT image, across patients and time points. To get exactly what we want, we use *linkers*.
All available linkers are located in the folder `. \avid\linkers`.

```python
# Link MR and CT images from the same patient and timepoint
patient_linker = CaseLinker() + TimePointLinker()
```


### Splitter & Sorter
There also exist **Splitters** and **Sorters** to offer even more possibilities to steer the behavior of actions. But for most simple workflows the defaults are just fine.
Therefore we ignore them for now. If you are interested to learn more please go to the respective tutorials and in depth documentation.


### Workflow Script
**Workflow scripts** declare what processing you want to happen with your data. They define the sequence of actions, selectors, and linkers etc. that transform your data.
The script shown in [Basic Example](#basic-example) is a very simple workflow script example.

## 📊 Real-world Example

Let's say you have a dataset with CT images, masks segmented on the CT images and  MR images from multiple patients across different timepoints, and you want to:
1. Register all MR images to the CT of the same patient/timestep
2. Calculate radiomics features for the MR images mapped to CT space using the respective masks
3. Only process complete patient datasets

```python
# Select CT images as targets, MR as moving images
ct_selector = ActionTagSelector('CT')
mask_selector = ActionTagSelector('CT_mask')
mr_selector = ActionTagSelector('MR')

# Link images from same patient/timepoint
patient_linker = CaseLinker() + TimePointLinker()

with session:
    # Register all MRs onto CTs for each patient/timepoint
    matcher = MitkMatchImageBatchAction(
        targetSelector=ct_selector,
        movingSelector=mr_selector,
        movingLinker=patient_linker,
        algorithm=path_to_the_used_reg_algorithm,
        actionTag="MR-CT-Reg"
    )

    # Map all MRs by the determined respective registration for each patient/timepoint
    mapper = MitkMapImageBatchAction(
        inputSelector=mr_selector,
        registrationSelector=registration.actionTagSelector,
        templateSelector=ct_selector,
        actionTag="Mapped_MR"
    )

    # Calculate features on mapped MR images
    MitkCLGlobalImageFeaturesBatchAction(
        imageSelector=mapper.actionTagSelector,
        maskSelector=mask_selector,
        actionTag="features"
    )
    session.run_batches()
```

AVID automatically:
- Finds all patient/timepoint combinations
- Only processes cases where both CT and MR exist
- Tracks all processing steps and metadata
- Scales from single cases to large cohorts

## 🔧 Available Actions

AVID provides numerous built-in actions for common image processing tasks:

- **Registration**: Rigid, affine, and deformable registration
- **Resampling**: Image resampling and spacing adjustment
- **Segmentation**: Integration with various segmentation tools
- **Radiomics**: Feature extraction from images and masks
- **Format conversion**: Between different medical image formats
- **Python actions**: Custom processing with full Python flexibility
- **CLI integration**: Easy integration of command-line tools

## 📁 Project Structure

```
your_project/
├── data/                    # Raw input data
├── output/                  # Processing results
│   ├── bootstrap.avid      # Initial data catalog
│   └── session.avid        # Full processing session
├── datacrawler.py          # Data discovery script
└── workflow.py             # Main processing workflow
```

## 🎓 Learning More

### Complete Tutorial
Check out our comprehensive Jupyter notebook tutorial: `examples/AVID_introduction.ipynb`


### Configuration
Configure AVID for your environment:
```bash
# Set tools path for external applications
avidconfig settings avid.toolspath /path/to/your/tools

# Install required tools (Windows)
avidconfig tools install
```

## 🤔 When to Choose AVID vs Other Workflow Tools

### Choose AVID when:
- ✅ **Dynamic data relationships**: Your workflow needs to automatically handle varying numbers of inputs per case (e.g., different patients have different numbers of timepoints or imaging modalities)
- ✅ **Complex data linking**: You need to pair/match data based on metadata (same patient, timepoint, modality combinations)
- ✅ **Biomedical imaging focus**: Working with medical images where patient-centric organization is crucial
- ✅ **Unpredictable data structure**: Your dataset structure varies and you want the workflow to adapt automatically
- ✅ **Metadata-driven processing**: The processing logic depends heavily on data properties rather than fixed file paths

### Choose Airflow when:
- 🔄 **Fixed DAGs**: You have well-defined, stable workflow structures
- 📅 **Scheduling focus**: You need complex scheduling, monitoring, and alerting capabilities
- 🏢 **Enterprise environment**: Working in environments requiring robust orchestration, user management, and web UI
- 🔗 **Service integration**: Heavy integration with databases, APIs, and external services

### Choose Nextflow when:
- 🧬 **Bioinformatics pipelines**: Primarily processing genomics/transcriptomics data
- ☁️ **Cloud-native**: Heavy focus on containerization and cloud deployment
- 📊 **High-throughput computing**: Need for automatic parallelization and resource management
- 🐳 **Container-first**: Workflows are primarily containerized tools

### Choose Snakemake when:
- 📁 **File-based workflows**: Processing follows clear input → output file patterns
- 🎯 **Make-like logic**: Comfortable with rule-based, target-driven execution
- 🐍 **Python ecosystem**: Want Python-based rules with minimal learning curve
- 🔄 **Reproducible science**: Focus on reproducibility with minimal overhead

**In summary**: Choose AVID when your data structure is dynamic and metadata-driven, especially in biomedical imaging where patient-centric organization and flexible data relationships are key requirements.

## 📋 Requirements

- Python 3.x
- Operating system independent (Windows, Linux, macOS)
- Optional: External tools for specific processing steps

## 📄 License

Copyright © German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC).
Please ensure your usage complies with the code license (see file LICENSE).

## 🆘 Support & Contributing

- 📖 **Documentation**: Full API documentation available
- 🐛 **Issues**: Report bugs and feature requests
- 💬 **Discussion**: Join our community for questions and tips
- 🔧 **Contributing**: We welcome contributions and custom actions

---

**Ready to streamline your image processing workflows?** Install AVID and check out our tutorial to get started!