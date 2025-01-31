# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

import sys
from pathlib import Path
from subprocess import run

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# -- Project information -----------------------------------------------------

project = "sphinxext-opengraph"
copyright = "2020, FIRST"
author = "WPILib"

# The full version, including alpha/beta/rc tags
release = "1.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinxext.opengraph",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = "sphinxext-opengraph"
html_logo = "_static/og-logo.png"
html_theme = "furo"


# -- Configuration for this theme --------------------------------------------

ogp_site_url = "https://sphinxext-opengraph.readthedocs.io/en/latest/"

# Configuration for testing but generally we use the defaults
# Uncomment lines to see their effect.
ogp_social_cards = {
    "site_url": "sphinxext-opengraph.readthedocs.io",
    # "image": "TODO: add another image to test",
    # "line_color": "#4078c0",
}

# Generate sample social media preview images
path_script = Path(
    __file__, "..", "..", "script", "generate_social_card_previews.py"
).resolve()
run(("python", path_script), check=False)  # NoQA: S603
