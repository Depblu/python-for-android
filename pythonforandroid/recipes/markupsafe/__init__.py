from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class MarkupsafeRecipe(PyProjectRecipe):
    version = '3.0.2'
    url = f'https://github.com/pallets/markupsafe/archive/refs/tags/{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'markupsafe'



recipe = MarkupsafeRecipe()
