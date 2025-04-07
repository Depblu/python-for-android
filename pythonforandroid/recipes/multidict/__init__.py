from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class MultidictRecipe(PyProjectRecipe):
    version = '6.3.2'
    url = f'https://github.com/aio-libs/multidict/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'multidict'



recipe = MultidictRecipe()
