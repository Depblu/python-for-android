from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pathlib import Path
import shutil
from os.path import join
from pythonforandroid.logger import info


class UJsonRecipe(CompiledComponentsPythonRecipe):
    version = '5.10.0'
    url = 'https://pypi.python.org/packages/source/u/ujson/ujson-{version}.tar.gz'
    stl_lib_name = "c++_shared"
    hostpython_prerequisites = ["setuptools","pip"]
    #depends = ["setuptools", "c++_shared"]
    depends = []

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        print("--------------------------------")
        print(arch)
        for attr, value in vars(self.ctx).items():
            print(f"{attr}: {type(value)} [{value}]")
        print("--------------------------------")

        for attr, value in vars(self.ctx.python_recipe).items():
            print(f"{attr}: {type(value)} [{value}]")
        print("--------------------------------")

        base_path = self.ctx.hostpython.rsplit('python3', 1)[0]
        env['PYTHONPATH'] = base_path + 'Lib/site-packages'
        env['UJSON_BUILD_NO_STRIP'] = '1'
        # 添加链接参数 "-Wl,--no-undefined" 和对 libpython3.11.so 的库依赖
        #env['LDFLAGS'] = f"{env.get('LDFLAGS', '')} -L{self.ctx.get_libs_dir(arch.arch)} -lpython3.11 -Wl,--no-undefined"
        env['LDFLAGS'] = f"{env.get('LDFLAGS', '')} -L/home/lius/.local/share/python-for-android/build/other_builds/python3/arm64-v8a__ndk_target_26/python3/android-build -lpython3.11 -Wl,--no-undefined"
        print(self.ctx.hostpython)
        #print(env['PYTHONPATH'])
        print(env)
        print("--------------------------------")
        print(self.ctx.get_libs_dir(arch.arch))
        print(self.ctx.get_python_install_dir(arch.arch))
        # 确保链接到 Python 的共享库
        #env['LDFLAGS'] = f"{env.get('LDFLAGS', '')} -L{self.ctx.get_libs_dir(arch.arch)} -lpython3.11"
        return env

    def build_arch(self, arch):
        super().build_arch(arch)

        info("Copying libc++_shared.so from NDK to libs directory")
        libcpp_path = f"{self.ctx.ndk.sysroot_lib_dir}/{arch.command_prefix}/libc++_shared.so"
        shutil.copyfile(libcpp_path, Path(self.ctx.get_libs_dir(arch.arch)) / "libc++_shared.so")


recipe = UJsonRecipe()
