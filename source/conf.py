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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import sphinx_rtd_theme
import recommonmark
from recommonmark.transform import AutoStructify



# -- Project information -----------------------------------------------------

project = 'OUCHub'
copyright = '2021, linzzz'
author = 'linzzz'

# The full version, including alpha/beta/rc tags
# release = '0.1'

######################################
primary_domain = 'cpp'

html_show_sphinx = False

sphinxemoji_style = 'twemoji'

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'sphinx'

######################################

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc','sphinx_rtd_theme', 'recommonmark', 'sphinxemoji.sphinxemoji']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command Line for these cases.
language = 'zh_CN'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

html_logo = 'images/logo/logo_1.png'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_options = {
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': 'black',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': -1,
    'includehidden': True,
    'titles_only': False,

}

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

html_css_files = ['custom.css']

# At the bottom of conf.py
# def setup(app):
#     app.add_config_value('recommonmark_config', {
#         #'url_resolver': lambda url: github_doc_root + url,
#         #'auto_toc_tree_section': 'Contents',
#         'enable_math': True,
#         'enable_inline_math': True,
#         'enable_eval_rst': True,
#     }, True)
#     app.add_transform(AutoStructify)

