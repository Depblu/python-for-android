from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class propcacheRecipe(PyProjectRecipe):
    version = '0.3.1'
    url = f'https://github.com/aio-libs/propcache/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'propcache'



recipe = propcacheRecipe()
