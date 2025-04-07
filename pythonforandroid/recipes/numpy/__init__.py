from pythonforandroid.recipe import Recipe, MesonRecipe
from pythonforandroid.logger import error
from pythonforandroid.logger import shprint
from os.path import join
import shutil
import sh

NUMPY_NDK_MESSAGE = "In order to build numpy, you must set minimum ndk api (minapi) to `24`.\n"


class NumpyRecipe(MesonRecipe):
    version = 'v2.2.4'
    url = 'git+https://github.com/numpy/numpy'
    #hostpython_prerequisites = ["Cython>=3.0.6", "scikit_build_core"]  # meson does not detects venv's cython
    hostpython_prerequisites = ["Cython>=3.0.6"]
    extra_build_args = ['-Csetup-args=-Dblas=none', '-Csetup-args=-Dlapack=none']
    need_stl_shared = True
    install_in_hostpython = True

    def get_recipe_meson_options(self, arch):
        print("liusssssssssssssssssss, get_recipe_meson_options")
        options = super().get_recipe_meson_options(arch)
        # Custom python is required, so that meson
        # gets libs and config files properly
        options["binaries"]["python"] = self.ctx.python_recipe.python_exe
        options["binaries"]["python3"] = self.ctx.python_recipe.python_exe
        options["properties"]["longdouble_format"] = "IEEE_DOUBLE_LE" if arch.arch in ["armeabi-v7a", "x86"] else "IEEE_QUAD_LE"
        return options

    def get_recipe_env(self, arch, **kwargs):
        print("liusssssssssssssssssss, get_recipe_env")
        env = super().get_recipe_env(arch, **kwargs)

        # _PYTHON_HOST_PLATFORM declares that we're cross-compiling
        # and avoids issues when building on macOS for Android targets.
        env["_PYTHON_HOST_PLATFORM"] = arch.command_prefix
        
        python3_recipe = Recipe.get_recipe("hostpython3", self.ctx)
        build_dir = python3_recipe.get_build_dir(arch.arch)
        dynload_dir = join(build_dir, "native-build", "build", "lib.linux-x86_64-3.11")
        print("/////////////", arch.arch)
        print("/////////////", python3_recipe)
        print("/////////////", build_dir)
        print("/////////////", dynload_dir)
        base_path = self.ctx.hostpython.rsplit('python3', 1)[0]
        #env['PYTHONPATH'] = env.get('PYTHONPATH', '') + ':' + base_path + 'Lib/site-packages' + ':' + dynload_dir

        # NPY_DISABLE_SVML=1 allows numpy to build for non-AVX512 CPUs
        # See: https://github.com/numpy/numpy/issues/21196
        env["NPY_DISABLE_SVML"] = "1"
        env["TARGET_PYTHON_EXE"] = join(Recipe.get_recipe(
                "python3", self.ctx).get_build_dir(arch.arch), "android-build", "python")
        return env

    def download_if_necessary(self):
        print("liusssssssssssssssssss, download_if_necessary")
        # NumPy requires complex math functions which were added in api 24
        if self.ctx.ndk_api < 24:
            error(NUMPY_NDK_MESSAGE)
            exit(1)
        super().download_if_necessary()

    def build_arch(self, arch):
        print("liusssssssssssssssssss, build_arch")
        env = self.get_recipe_env(arch)
        
        print(shprint(sh.Command(self.ctx.hostpython), '-s', '-m', 'site', _env=env))
        
        super().build_arch(arch)
        self.restore_hostpython_prerequisites(["cython"])

    def get_hostrecipe_env(self, arch):
        print("liusssssssssssssssssss, get_hostrecipe_env")
        env = super().get_hostrecipe_env(arch)
        env['RANLIB'] = shutil.which('ranlib')
        env["LDFLAGS"] += " -lm"
        return env


recipe = NumpyRecipe()
