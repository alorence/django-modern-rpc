# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from os.path import abspath, join, dirname
import warnings
sys.path.insert(0, abspath(join(abspath(dirname(__file__)), '../..')))

try:
    import sphinx_rtd_theme  # noqa : F401
    sphinx_rtd = "sphinx_rtd_theme"
except ImportError:
    # Use ReadTheDocs default theme only if it is installed.
    # Simply install it via ``pip install sphinx_rtd_theme``
    warnings.warn("Please install 'sphinx_rtd_theme' in order to build the documentation")
    sphinx_rtd = None

import modernrpc  # noqa: F402
from django.conf import settings  # noqa: F402
settings.configure()

# -- Project information -----------------------------------------------------

# General information about the project.
project = 'django-modern-rpc'
copyright = '2016, Antoine Lorence'
author = 'Antoine Lorence'

# The full version, including alpha/beta/rc tags
release = modernrpc.__version__
# The short X.Y version.
version = release.rsplit('.', 1)[0]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = sphinx_rtd or 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
