from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class mmh3Recipe(PyProjectRecipe):
    version = '5.1.0'
    url = f'https://github.com/hajimes/mmh3/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'mmh3'



recipe = mmh3Recipe()
