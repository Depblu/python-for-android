from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class duckduckgo_searchRecipe(PyProjectRecipe):
    version = '8.0.0'
    url = f'https://github.com/deedy5/duckduckgo_search/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'duckduckgo_search'
    patches = ['pyproject_toml.patch']



recipe = duckduckgo_searchRecipe()
