from pythonforandroid.recipe import RustCompiledComponentsRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class RpdsRecipe(RustCompiledComponentsRecipe):
    version = '0.24.0'
    url = f'https://github.com/crate-py/rpds/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'rpds-py'



recipe = RpdsRecipe()
