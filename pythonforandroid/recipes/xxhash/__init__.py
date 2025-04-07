from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class XxhashRecipe(PyProjectRecipe):
    version = 'v3.5.0'
    url = f'git+https://github.com/ifduyue/python-xxhash.git'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'xxhash'




recipe = XxhashRecipe()
