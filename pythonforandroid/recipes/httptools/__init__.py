from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class HttptoolsRecipe(CompiledComponentsPythonRecipe):
    name = 'httptools'
    version = 'v0.6.4'
    url = 'git+https://github.com/MagicStack/httptools.git'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        # env['CFLAGS'] += openssl_recipe.include_flags(arch)
        # env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        # env['LIBS'] = openssl_recipe.link_libs_flags()

        return env



recipe = HttptoolsRecipe()
