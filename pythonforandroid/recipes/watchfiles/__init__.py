from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class watchfilesRecipe(RustCompiledComponentsRecipe):
    version = '1.0.4'
    url = f'https://github.com/samuelcolvin/watchfiles/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'watchfiles'



recipe = watchfilesRecipe()
