# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata
import sys
from pathlib import Path

from django.conf import settings

settings.configure()

root = Path("..").resolve()
sys.path.insert(0, str(root))

# -- Project information ------------------------------------------------------

# General information about the project.
project = "django-modern-rpc"
project_copyright = "2025"
author = "Antoine Lorence"

# The full version, including alpha/beta/rc tags
release = importlib.metadata.version("django-modern-rpc")
# The short X.Y version.
version = release.rsplit(".", 1)[0]

# The base URL which points to the root of the HTML documentation. It is used to indicate the
# location of document using the Canonical Link Relation
html_baseurl = "https://django-modern-rpc.readthedocs.io/"

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.autosectionlabel",
    "myst_parser",
    "sphinx_inline_tabs",
    "sphinx_design",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "Thumbs.db",
    ".DS_Store",
    "drafts/*",
]

# Suppress warnings about duplicated labels
suppress_warnings = ["autosectionlabel.*"]
# Enable todos blocks
todo_include_todos = True

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
templates_path = ["_templates"]
html_permalinks_icon = '<img src="/_static/permalink.svg" class="permalink-icon"/>'
# All (**) pages will have 1 more sidebar content (donation.html) after the default one (sbt-sidebar-nav.html)
# See https://sphinx-book-theme.readthedocs.io/en/stable/sections/sidebar-primary.html
html_sidebars = {"**": ["sbt-sidebar-nav.html", "donation.html"]}
html_theme_options = {
    "home_page_in_toc": True,
    "show_toc_level": 2,
    "toc_title": "Navigation",
    "use_download_button": False,
    "use_repository_button": True,
    "repository_url": "https://github.com/alorence/django-modern-rpc",
    "path_to_docs": "docs",
    "repository_branch": "main",
    "analytics": {
        "google_analytics_id": "G-7KF8EXTF4W",
    },
    "announcement": (
        "⚠️ This documentation is only applicable to the upcoming v2, currently in "
        "beta. If you installed a stable version of django-modern-rpc, please refer "
        'to <a href="https://django-modern-rpc.readthedocs.io/v1.1.0/">this page.</a>.'
    ),
    "icon_links": [],
}

# -- MyST Parser configuration ----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "tasklist",
]
myst_heading_anchors = 3

# -- Autodoc configuration ---------------------------------------------------
autodoc_typehints = "description"
autodoc_member_order = "bysource"
