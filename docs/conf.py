# -- General configuration ------------------------------------------------

import os

if not os.environ.get('READTHEDOCS', None):
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

master_doc = 'index'
exclude_patterns = ['_build']

# General information about the project.
project = u'Supermann'
copyright = u'2014, Sam Clements'
version = '3.0.0'
release = '3.0.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode'
]
autodoc_member_order = 'bysource'
autoclass_content = 'both'
