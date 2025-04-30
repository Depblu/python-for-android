from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe, NDKRecipe, Recipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint
import sh
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
from pythonforandroid.logger import (
    logger, info, warning, debug, shprint, info_main, error)
import glob

class onnxruntimeRecipe(PyProjectRecipe):
    version = '1.21.0'
    url = f'git+https://github.com/microsoft/onnxruntime.git'
    depends = ['numpy', 'python3_link_dep']
    patches = ['patches/p4a_build_debug.patch']
    #hostpython_prerequisites = ['setuptools', 'wheel']
    #site_packages_name = 'onnxruntime'
    build_config = 'MinSizeRel'

    def download_if_necessary(self):
        info_main('Downloading {}'.format(self.name))
        with current_directory(join(self.ctx.packages_path, self.name)):
            filename = shprint(sh.basename, self.url).stdout[:-1].decode('utf-8')
            print("lius debug log: ", filename)
            if exists(filename) and isdir(filename):
                info(f'{filename} existed,  skipping download for {self.name}')
                return
        self.download()


    # 
    def should_build_internel(self, arch):
        # 使用glob查找wheel文件
        with current_directory(join(self.get_build_dir(arch.arch))):
            res = glob.glob(f"p4a_android_build/{self.build_config}/dist/*.whl")
            print("liusdebug", res)
            
            built_wheels = [realpath(whl) for whl in glob.glob(f"p4a_android_build/{self.build_config}/dist/*.whl")]
            if built_wheels:
                info(f'find onnxruntime wheel files: {built_wheels}, skip building')
                return False
        return True

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'build', 'lib', arch.arch)
    
    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["http_proxy"] = "http://127.0.0.1:7890"
        env["https_proxy"] = "http://127.0.0.1:7890"
        env["HTTP_PROXY"] = "http://127.0.0.1:7890"
        env["HTTPS_PROXY"] = "http://127.0.0.1:7890"
        env["ALL_PROXY"] = "http://127.0.0.1:7890"
        env["all_proxy"] = "http://127.0.0.1:7890"
        env['ANDROID_NDK'] = self.ctx.ndk_dir
        env['ANDROID_SDK'] = self.ctx.sdk_dir
        env['ANDROID_API'] = str(self.ctx.android_api)
        #env['PATH'] = "/home/lius/.local/share/python-for-android/build/other_builds/hostpython3/desktop/hostpython3/native-build" + ":" + env['PATH']
        return env

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        

    def build_arch(self, arch):
        build_dir = join(self.get_build_dir(arch.arch))
        ensure_dir(build_dir)

        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            
            print("////////// env export commands:")
            for key, value in env.items():
                print(f"export {key}='{value}'")
            print("/////////////")
            
            python_major = self.ctx.python_recipe.version[0]
            python_build_dir = self.ctx.python_recipe.get_build_dir(arch.arch)
            python_include_root = self.ctx.python_recipe.include_root(arch.arch)
            python_site_packages = self.ctx.get_site_packages_dir(arch)
            python_link_root = self.ctx.python_recipe.link_root(arch.arch)
            python_link_version = self.ctx.python_recipe.link_version
            python_library = join(python_link_root,
                                  'libpython{}.so'.format(python_link_version))
            python_include_numpy = join(python_site_packages,
                                        'numpy', '_core', 'include')
            
            numpy_build_dir = Recipe.get_recipe('numpy', self.ctx).get_build_dir(arch.arch)
            
            ndk_dir = self.ctx.ndk_dir

            print(f"lius debug log : ndk_dir = {ndk_dir}")
            
            PYTHON_CORE_ROOT1=f"{python_build_dir}"
            PYTHON_CORE_ROOT2=f"{python_link_root}"
            NUMPY_SITE_PACKAGES=f"{numpy_build_dir}"


            print(f"lius debug log : build_dir = {build_dir}")
            print(f"lius debug log : env = {env}")
            print(f"lius debug log : python_major = {python_major}")
            print(f"lius debug log : python_include_root = {python_include_root}")
            print(f"lius debug log : python_site_packages = {python_site_packages}")
            print(f"lius debug log : python_link_root = {python_link_root}")
            print(f"lius debug log : python_link_version = {python_link_version}")
            print(f"lius debug log : python_library = {python_library}")
            print(f"lius debug log : python_include_numpy = {python_include_numpy}")
            print(f"lius debug log : numpy_build_dir = {numpy_build_dir}")
            print(f"lius debug log : hostpython = {self.ctx.hostpython}")

            if self.should_build_internel(arch):
                shprint(sh.Command(f"{build_dir}/build.sh"), 
                        '--config', f'{self.build_config}',
                        '--android', 
                        '--android_abi', 'arm64-v8a', 
                        '--android_sdk_path', env['ANDROID_SDK'], 
                        '--android_api', env['ANDROID_API'], 
                        '--android_ndk_path', env['ANDROID_NDK'], 
                        '--android_cpp_shared', 
                        '--enable_pybind', 
                        '--build_wheel', 
                        '--build_dir', f'{build_dir}/p4a_android_build', 
                        '--cmake_extra_defines', 
                        f"CMAKE_PREFIX_PATH={PYTHON_CORE_ROOT1};{PYTHON_CORE_ROOT2};{NUMPY_SITE_PACKAGES}",
                        f"PYTHON_INCLUDE_DIR={python_include_root}",
                        #f"PYTHON_LIBRARY={python_link_root}/libpython{python_link_version}.so",
                        f"Python_NumPy_INCLUDE_DIRS={numpy_build_dir}/numpy/_core/include;{numpy_build_dir}/p4a_android_build/numpy/_core",
                        f"Python_FIND_STRATEGY='LOCATION'",
                        f"PYTHON_EXECUTABLE={self.ctx.hostpython}",
                        f"CMAKE_HTTP_PROXY=http://127.0.0.1:7890",
                        f"CMAKE_HTTPS_PROXY=http://127.0.0.1:7890",
                        _env=env)
            
            built_wheels = [realpath(whl) for whl in glob.glob(f"p4a_android_build/{self.build_config}/dist/*.whl")]
            self.install_wheel(arch, built_wheels)
            
            
            
            

recipe = onnxruntimeRecipe()
