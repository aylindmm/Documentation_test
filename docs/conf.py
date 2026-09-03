# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'aTUNApy'
copyright = '2026, Aylin del Moral-Morales'
author = 'Aylin del Moral-Morales'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",     # Google-style docstrings
    "sphinx.ext.viewcode",     # optional: "[source]" links
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

napoleon_google_docstring = True
napoleon_numpy_docstring = False
autodoc_member_order = "bysource"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

# "Edit on GitHub" link in the top-right
html_context = {
    "display_github": True,
    "github_user": "YOUR_GITHUB_USERNAME",
    "github_repo": "autoDB",
    "github_version": "main",      # your default branch
    "conf_py_path": "/docs/",      # path to the folder containing conf.py
}

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
}
