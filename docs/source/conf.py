# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = "AVID"
copyright = "2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)"
author = (
    "German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)"
)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "myst_parser",
]
# sphinx-apidoc ./avid/ -o ./docs/source/avid/ -f -E

templates_path = ["_templates"]
exclude_patterns = [
    "actions/unrefactored/*",
]

myst_heading_anchors = 3


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
