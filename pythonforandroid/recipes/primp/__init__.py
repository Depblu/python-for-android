from pythonforandroid.recipe import RustCompiledComponentsRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class primpRecipe(RustCompiledComponentsRecipe):
    version = '0.14.0'
    url = f'https://github.com/deedy5/primp/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'primp'

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env['ANDROID_NDK_HOME'] = self.ctx.ndk_dir

        return env


recipe = primpRecipe()
