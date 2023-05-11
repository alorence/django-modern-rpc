# flake8: noqa
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pkg_resources

from django.conf import settings

settings.configure()

# -- Project information ------------------------------------------------------

# General information about the project.
project = "django-modern-rpc"
copyright = "2022"
author = "Antoine Lorence"

# The full version, including alpha/beta/rc tags
release = pkg_resources.get_distribution("django-modern-rpc").version
# The short X.Y version.
version = release.rsplit(".", 1)[0]

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "myst_parser",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "drafts/*",
]

html_baseurl = "https://django-modern-rpc.readthedocs.io/"

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
html_theme = "sphinx_book_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Theme options ------------------------------------------------------------
html_title = "django-modern-rpc"
html_css_files = ["custom.css"]
html_permalinks_icon = (
    '<img src="/_static/permalink.svg" style="height: 0.75em; margin-bottom: 0.15em"/>'
)
html_theme_options = {
    "home_page_in_toc": True,
    "show_toc_level": 1,
    "toc_title": "Navigation",
    "use_download_button": False,
    "use_repository_button": True,
    "repository_url": "https://github.com/alorence/django-modern-rpc",
    "analytics": {
        "google_analytics_id": "G-7KF8EXTF4W",
    },
}
