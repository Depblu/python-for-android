from pythonforandroid.recipe import CythonRecipe, PyProjectRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class yarlRecipe(PyProjectRecipe):
    version = '1.19.0'
    url = f'https://github.com/aio-libs/yarl/archive/refs/tags/v{version}.tar.gz'
    #depends = ["python3", "cython", 'setuptools']
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'yarl'

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        print("lius ......", env)
        env["YARL_NO_EXTENSIONS"] = "1"
        
        return env

recipe = yarlRecipe()
