from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class wraptRecipe(CompiledComponentsPythonRecipe):
    name = 'wrapt'
    version = '1.17.1'
    url = f'https://github.com/GrahamDumpleton/wrapt/archive/refs/tags/{version}.tar.gz'
    depends = []
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        # env['CFLAGS'] += openssl_recipe.include_flags(arch)
        # env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        # env['LIBS'] = openssl_recipe.link_libs_flags()

        return env


recipe = wraptRecipe()
