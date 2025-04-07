from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class FrozenlistRecipe(PyProjectRecipe):
    version = '1.5.0'
    url = f'https://github.com/aio-libs/frozenlist/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'frozenlist'



recipe = FrozenlistRecipe()
