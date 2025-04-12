from pythonforandroid.recipe import RustCompiledComponentsRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class orjsonRecipe(RustCompiledComponentsRecipe):
    version = '3.10.16'
    url = f'https://github.com/ijl/orjson/archive/refs/tags/{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'orjson'

        

recipe = orjsonRecipe()
