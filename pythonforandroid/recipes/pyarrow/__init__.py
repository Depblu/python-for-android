from pythonforandroid.recipe import PyProjectRecipe, Recipe
from pathlib import Path
import shutil
from os.path import join, exists
from pythonforandroid.logger import info, warning, error
import shlex
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
from pythonforandroid.logger import shprint
import sh


def ensure_file_link(source: str, target: str):
    """
    确保目标文件是源文件的软链接。
    
    参数:
        source: 源文件路径
        target: 目标软链接路径
    """
    if not exists(source):
        error(f"源文件不存在: {source}")
        return
    
    if exists(target):
        if (isfile(target) or isdir(target)) and realpath(target) == realpath(source):
            info(f"已经存在软链接: {target} -> {source}")
        else:
            error(f"目标文件或目录存在但不是指向源文件的软链接: {target}")
    else:
        info(f"创建软链接: {target} -> {source}")
        shprint(sh.Command('ln'), '-s', source, target)

class PyarrowRecipe(PyProjectRecipe):
    name = 'pyarrow'
    version = '19.0.1'
    url = f'https://files.pythonhosted.org/packages/source/p/pyarrow/pyarrow-{version}.tar.gz'
    #depends = ['libarrow_cpp', 'numpy']
    depends = ['libarrow_cpp']
    patches = ['setup_py.patch', 'cmakelists.patch', 'find_python_cmake.patch']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env['CHARSET_NORMALIZER_USE_MYPYC'] = "1"

        # --- BEGIN WORKAROUND for Arrow C++ dependency ---
        info("Attempting to manually set CMAKE_PREFIX_PATH for pyarrow dependency on libarrow_cpp")
        try:
            libarrow_cpp_recipe = self.get_recipe('libarrow_cpp', self.ctx)
            # Use get_build_dir instead of get_install_dir, install_dir might be generic
            # arrow_install_prefix = libarrow_cpp_recipe.get_install_dir(arch) # This might point too generally
            # Let's try constructing the path based on known structure
            libarrow_cpp_build_dir = libarrow_cpp_recipe.get_build_dir(arch.arch)
            arrow_install_prefix = join(libarrow_cpp_build_dir, 'dist')

            info(f"Calculated Arrow C++ install prefix: {arrow_install_prefix}")

            # Define the expected location of the CMake config file
            arrow_cmake_dir = join(arrow_install_prefix, 'lib', 'cmake', 'Arrow')
            expected_cmake_file = join(arrow_cmake_dir, 'ArrowConfig.cmake')

            if not exists(expected_cmake_file):
                error(f"Arrow CMake config file NOT FOUND at expected location: {expected_cmake_file}")
            else:
                info(f"Confirmed Arrow CMake config file exists at: {expected_cmake_file}")

            if arrow_cmake_dir and exists(arrow_cmake_dir):
                 info(f"Setting CMAKE_PREFIX_PATH to include: {arrow_install_prefix}")
                 # Prepend the path to ensure it's searched first
                 existing_cmake_path = env.get('CMAKE_PREFIX_PATH', '')
                 env['CMAKE_PREFIX_PATH'] = f"{arrow_install_prefix};{existing_cmake_path}".strip(';')

                 info(f"Setting Arrow_DIR to: {arrow_cmake_dir}")
                 # Explicitly set Arrow_DIR as a fallback/primary hint
                 env['Arrow_DIR'] = arrow_cmake_dir
            else:
                warning("Skipping CMAKE_PREFIX_PATH/Arrow_DIR injection because Arrow CMake directory could not be confirmed.")

        except Exception as e:
            warning(f"Error trying to get libarrow_cpp recipe or path: {e}")
            warning("CMAKE_PREFIX_PATH/Arrow_DIR injection skipped due to error.")
        # --- END WORKAROUND ---


        # python3
        python3_include_root = self.ctx.python_recipe.include_root(arch.arch)
        python3_link_root = self.ctx.python_recipe.link_root(arch.arch)
        python3_link_version = self.ctx.python_recipe.link_version
        python3_lib = f'{python3_link_root}/libpython{python3_link_version}.so'
        
        env['PYTHONINCLUDE'] = python3_include_root
        env['CPYTHONLIB'] = python3_lib

        numpy_build_dir = Recipe.get_recipe('numpy', self.ctx).get_build_dir(arch.arch)

        # --- Step 3: Inject CMake arguments via PYARROW_CMAKE_OPTIONS ---
        info("Preparing PYARROW_CMAKE_OPTIONS with cross-compiling and Python hints")
        cmake_options_list = [] # Use a list to build the options

        ndk_dir = self.ctx.ndk_dir
        ndk_api = self.ctx.ndk_api
        ndk_toolchain_file = join(ndk_dir, 'build', 'cmake', 'android.toolchain.cmake')
        ndk_sysroot = f'{ndk_dir}/toolchains/llvm/prebuilt/linux-x86_64/sysroot/home'
        target_python_prefix = python3_link_root
        
        # Add cross-compilation hints if found
        # The NDK toolchain file is the most robust way
        if ndk_toolchain_file:
             cmake_options_list.append(f"-DCMAKE_TOOLCHAIN_FILE={shlex.quote(ndk_toolchain_file)}")
        if ndk_sysroot: # Sysroot might be set by toolchain, but can be explicit
             cmake_options_list.append(f"-DCMAKE_SYSROOT={shlex.quote(ndk_sysroot)}")

        # Set find root path (semicolon-separated for CMake list)
        find_roots = filter(None, [ndk_sysroot, target_python_prefix, arrow_install_prefix, numpy_build_dir])
        if find_roots:
             # 将filter对象转换为列表并用分号连接
             find_roots_list = list(find_roots)
             find_roots_str = ";".join(find_roots_list).strip(';')
             cmake_options_list.append(f"-DCMAKE_FIND_ROOT_PATH={find_roots_str}")
             # Force CMake to search ONLY in the find_root_path for dependencies
             cmake_options_list.append("-DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER")
             cmake_options_list.append("-DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY")
             cmake_options_list.append("-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY")
             cmake_options_list.append("-DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY")

        # Add Arrow hints (as fallback/extra info)
        cmake_options_list.append(f"-DArrow_DIR={shlex.quote(env['Arrow_DIR'])}")

        # Force FindPython strategy
        cmake_options_list.append("-DPython3_FIND_STRATEGY=LOCATION")
        

        # --- Adjust CMAKE_PREFIX_PATH for NumPy ---
        # Also add potential NumPy related paths to CMAKE_PREFIX_PATH as a fallback mechanism
        # for CMake finding NumPy components or other dependencies.
        
        
        current_cmake_prefix_path = env.get('CMAKE_PREFIX_PATH', '')
        potential_numpy_prefixes = []
        numpy_core_path = join(numpy_build_dir, 'p4a_android_build', 'numpy', 'core')
        numpy_underscore_core_path = join(numpy_build_dir, 'p4a_android_build', 'numpy', '_core')

        if exists(numpy_core_path):
             potential_numpy_prefixes.append(numpy_core_path)
        if exists(numpy_underscore_core_path):
             potential_numpy_prefixes.append(numpy_underscore_core_path)
        # Optionally add the parent numpy directory as well
        if exists(join(numpy_build_dir, 'numpy')):
             potential_numpy_prefixes.append(join(numpy_build_dir, 'numpy'))


        if potential_numpy_prefixes:
             # Ensure paths are unique and filter out empty strings
             unique_numpy_paths = list(filter(None, dict.fromkeys(potential_numpy_prefixes)))
             if unique_numpy_paths:
                  added_paths_str = ';'.join(unique_numpy_paths)
                  env['CMAKE_PREFIX_PATH'] = f"{current_cmake_prefix_path};{added_paths_str}".strip(';')
                  info(f"Added NumPy related paths to CMAKE_PREFIX_PATH: {added_paths_str}")


        # f"CMAKE_PREFIX_PATH={PYTHON_CORE_ROOT1};{PYTHON_CORE_ROOT2};{NUMPY_SITE_PACKAGES}",
        # f"PYTHON_INCLUDE_DIR={python_include_root}",
        # f"PYTHON_LIBRARY={python_link_root}/libpython{python_link_version}.so",
        # f"Python_NumPy_INCLUDE_DIRS={numpy_build_dir}/numpy/_core/include;{numpy_build_dir}/p4a_android_build/numpy/_core",
        # f"Python_FIND_STRATEGY='LOCATION'",
        # f"PYTHON_EXECUTABLE={self.ctx.hostpython}",
        
        python_build_dir = self.ctx.python_recipe.get_build_dir(arch.arch)
        python_link_root = self.ctx.python_recipe.link_root(arch.arch)
        python_include_root = self.ctx.python_recipe.include_root(arch.arch)
        python_link_version = self.ctx.python_recipe.link_version
        PYTHON_CORE_ROOT1=f"{python_build_dir}"
        PYTHON_CORE_ROOT2=f"{python_link_root}"
        NUMPY_SITE_PACKAGES=f"{numpy_build_dir}"
        cmake_options_list.append(f"-DCMAKE_PREFIX_PATH={PYTHON_CORE_ROOT1};{PYTHON_CORE_ROOT2};{NUMPY_SITE_PACKAGES};{env['CMAKE_PREFIX_PATH']}")
        cmake_options_list.append(f"-DPYTHON3_INCLUDE_DIRS={python_include_root}")
        cmake_options_list.append(f"-DPYTHON3_LIBRARIES={python_link_root}/libpython{python_link_version}.so")
        #cmake_options_list.append(f"-DPython3_NumPy_INCLUDE_DIRS={numpy_build_dir}/numpy/_core/include;{numpy_build_dir}/p4a_android_build/numpy/_core")
        cmake_options_list.append(f"-DPython3_NumPy_INCLUDE_DIRS={numpy_build_dir}/numpy/_core/include")
        cmake_options_list.append(f'-DPython3_FIND_STRATEGY="LOCATION"')
        cmake_options_list.append(f"-DPYTHON3_EXECUTABLE={self.ctx.hostpython}")
        cmake_options_list.append(f"-DANDROID_ABI={arch.arch}")
        cmake_options_list.append(f"-DANDROID_PLATFORM=android-{ndk_api}")
        cmake_options_list.append(f"-DPython3_NumPy_FOUND=TRUE")
        cmake_options_list.append(f"-DPython3_FOUND=TRUE")
        cmake_options_list.append(f'-DCMAKE_C_FLAGS="-I{numpy_build_dir}/numpy/_core/include -I{numpy_underscore_core_path}"')
        cmake_options_list.append(f'-DCMAKE_CXX_FLAGS="-I{numpy_build_dir}/numpy/_core/include -I{numpy_underscore_core_path}"')
        

        # Combine options into the correct environment variable, properly quoted if needed
        env['PYARROW_CMAKE_OPTIONS'] = " ".join(cmake_options_list)


        info(f"Final CMAKE_PREFIX_PATH for pyarrow build: {env.get('CMAKE_PREFIX_PATH', 'Not Set')}")
        info(f"Final Arrow_DIR for pyarrow build: {env.get('Arrow_DIR', 'Not Set')}")
        info(f"Final PYTHONINCLUDE hint: {env.get('PYTHONINCLUDE', 'Not Set')}")
        info(f"Final CPYTHONLIB hint: {env.get('CPYTHONLIB', 'Not Set')}")
        return env


recipe = PyarrowRecipe()


