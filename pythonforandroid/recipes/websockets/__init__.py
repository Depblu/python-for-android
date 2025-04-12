from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class websocketsRecipe(PyProjectRecipe):
    version = '15.0.1'
    url = f'https://github.com/python-websockets/websockets/archive/refs/tags/{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'websockets'

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["BUILD_EXTENSION"] = "1"
        return env

recipe = websocketsRecipe()
