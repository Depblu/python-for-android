from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pathlib import Path
import shutil
from os.path import join
from pythonforandroid.logger import info


class GrpcioToolsRecipe(CompiledComponentsPythonRecipe):
    version = '1.71.0'
    url = f'https://files.pythonhosted.org/packages/source/g/grpcio_tools/grpcio_tools-{version}.tar.gz'
    stl_lib_name = "c++_shared"
    #hostpython_prerequisites = ["setuptools","pip"]

    depends = ['python3', 'protobuf', 'grpcio', 'setuptools']
    site_packages_name = 'grpcio-tools'
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

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
        
        python_build_dir = self.ctx.python_recipe.get_build_dir(arch.arch)
        

        base_path = self.ctx.hostpython.rsplit('python3', 1)[0]
        env['PYTHONPATH'] = base_path + 'Lib/site-packages'
        
        env['GRPC_PYTHON_CFLAGS'] = env['CFLAGS']
        
        # 添加链接参数 "-Wl,--no-undefined" 和对 libpython3.11.so 的库依赖
        #env['LDFLAGS'] = f"{env.get('LDFLAGS', '')} -L{self.ctx.get_libs_dir(arch.arch)} -lpython3.11 -Wl,--no-undefined"
        env['LDFLAGS'] = f"{env.get('LDFLAGS', '')} -L{python_build_dir}/android-build -lpython3.11 -llog -Wl,--no-undefined"
        
        env['GRPC_PYTHON_LDFLAGS'] = env['LDFLAGS']
        
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


recipe = GrpcioToolsRecipe()
