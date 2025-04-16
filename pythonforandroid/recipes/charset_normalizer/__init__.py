from pythonforandroid.recipe import PyProjectRecipe, Recipe
from pathlib import Path
import shutil
from os.path import join
from pythonforandroid.logger import info









class CharsetNormalizerRecipe(PyProjectRecipe):
    name = 'charset_normalizer'
    version = '3.4.1'
    url = 'https://github.com/jawah/charset_normalizer/archive/refs/tags/{version}.tar.gz'

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch)
        env['CHARSET_NORMALIZER_USE_MYPYC'] = "1"
        return env


recipe = CharsetNormalizerRecipe()


