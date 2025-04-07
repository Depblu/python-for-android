from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class PyyamlRecipe(PyProjectRecipe):
    version = '6.0.2'
    url = f'https://github.com/yaml/pyyaml/archive/refs/tags/{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'pyyaml'



recipe = PyyamlRecipe()
