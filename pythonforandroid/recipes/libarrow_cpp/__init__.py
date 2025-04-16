from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory, ensure_dir, BuildInterruptingException
from multiprocessing import cpu_count
from os.path import join
import sh
import shutil
from os import environ
from pythonforandroid.util import build_platform, rmdir
import os
from pythonforandroid.logger import info

arch_to_sysroot = {'armeabi': 'arm', 'armeabi-v7a': 'arm', 'arm64-v8a': 'arm64'}


def arch_to_toolchain(arch):
    if 'arm' in arch.arch:
        return arch.command_prefix
    return arch.arch


class ArrowCppRecipe(Recipe):

    name = 'libarrow_cpp'
    version = '19.0.1'
    url = 'git+https://github.com/apache/arrow.git'
    libdir = 'dist/lib'
    built_libraries = {'libarrow.so': libdir}
    patches = ['tz_visibility.patch', 're2_utf8proc_cmake.patch']


    def download_if_necessary(self):
         # 检查版本号是否以'apache-arrow-'开头，如果不是则添加前缀
         if not self.version.startswith('apache-arrow-'):
             self._version = 'apache-arrow-' + self.version
         return super().download_if_necessary()


    def prebuild_arch(self, arch):
        """
        Initialize Git submodules before running CMake.
        Arrow uses submodules for some bundled dependencies (like utf8proc, re2)
        and potentially testing data (though we disable tests).
        """
        super().prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        # Make sure we are in the root of the extracted source directory
        if os.path.exists(os.path.join(build_dir, 'cpp', 'CMakeLists.txt')):
             # Need to be in the main git repo root before running submodule command
             shprint(sh.git, 'submodule', 'update', '--init', '--recursive', _cwd=build_dir)
        else:
             self.warning(f"Could not find cpp/CMakeLists.txt in {build_dir}, "
                          "skipping submodule update. This might cause issues "
                          "if bundled dependencies are needed.")

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['ARROW_HOME'] = join(self.get_build_dir(arch.arch), 'dist')
        env['LD_LIBRARY_PATH'] = join(env['ARROW_HOME'], 'lib') + ':' + env.get('LD_LIBRARY_PATH', '')
        env['CMAKE_PREFIX_PATH'] = env['ARROW_HOME'] + ':' + env.get('CMAKE_PREFIX_PATH', '')
        env['VERBOSE'] = '1'
        env['https_proxy'] = 'http://127.0.0.1:7890'
        env['http_proxy'] = 'http://127.0.0.1:7890'

        return env

    def get_arrow_cmake_args_v2(self, arch):
            """
            Helper function to generate Arrow-specific CMake arguments.
            Does NOT include standard p4a args like toolchain or install prefix.
            """
            # install_dir = self.get_install_dir(arch.arch) # Not needed here, p4a handles CMAKE_INSTALL_PREFIX

            arrow_cmake_args = []

            # --- Arrow Feature Flags ---
            arrow_cmake_args.extend([
                '-DARROW_BUILD_TESTS=OFF',
                '-DARROW_BUILD_BENCHMARKS=OFF',
                '-DARROW_BUILD_EXAMPLES=OFF',
                '-DARROW_BUILD_UTILITIES=OFF',
                '-DARROW_PYTHON=OFF',
                '-DARROW_INSTALL_NAME_RPATH=OFF',

                # Disable complex/optional components
                '-DARROW_CUDA=OFF',
                '-DARROW_DATASET=OFF', # Keep minimal for now
                '-DARROW_FLIGHT=OFF',
                '-DARROW_GANDIVA=OFF',
                '-DARROW_HDFS=OFF',
                '-DARROW_ORC=OFF',
                '-DARROW_PARQUET=OFF',
                '-DARROW_SUBSTRAIT=OFF',
                '-DARROW_ACERO=OFF',
                '-DARROW_S3=OFF',
                '-DARROW_GCS=OFF',
                '-DARROW_AZURE=OFF',
            ])

            # Enable core components
            arrow_cmake_args.extend([
                '-DARROW_COMPUTE=ON',
                '-DARROW_FILESYSTEM=ON',
                '-DARROW_IPC=ON',
                '-DARROW_CSV=ON',
                '-DARROW_JSON=ON',
            ])

            # --- Dependency Handling ---
            #arrow_cmake_args.append('-DARROW_DEPENDENCY_SOURCE=SYSTEM')
            arrow_cmake_args.append('-DARROW_WITH_ZLIB=ON' if 'zlib' in self.depends else 'OFF')
            arrow_cmake_args.append('-DARROW_WITH_LZ4=ON' if 'lz4' in self.depends else 'OFF')
            arrow_cmake_args.append('-DARROW_WITH_ZSTD=ON' if 'zstd' in self.depends else 'OFF')
            arrow_cmake_args.append('-DARROW_WITH_BROTLI=ON' if 'brotli' in self.depends else 'OFF')
            arrow_cmake_args.append('-DARROW_WITH_SNAPPY=OFF')
            arrow_cmake_args.append('-DARROW_WITH_BZ2=OFF')
            arrow_cmake_args.append('-DARROW_WITH_OPENSSL=OFF')
            arrow_cmake_args.append('-DARROW_WITH_BOOST=OFF')

            # Use bundled for simple internal deps unless recipes exist and are preferred
            arrow_cmake_args.extend([
                '-DARROW_WITH_RE2=BUNDLED',
                '-DARROW_WITH_UTF8PROC=BUNDLED',
            ])

            # --- Build & Install Options ---
            arrow_cmake_args.extend([
                '-DCMAKE_INSTALL_LIBDIR=lib',
                '-DARROW_SIMD_LEVEL=NONE',
                '-DARROW_RUNTIME_SIMD_LEVEL=NONE',
                '-DARROW_USE_CCACHE=OFF',
                # '-DCMAKE_UNITY_BUILD=ON', # Consider enabling later
            ])

            # IMPORTANT: Specify the source directory containing the main C++ CMakeLists.txt
            # The source checkout root is self.get_build_dir(arch.arch)
            source_dir_cpp = os.path.join(self.get_build_dir(arch.arch), "cpp")
            arrow_cmake_args.append(f'-S{source_dir_cpp}')

            return arrow_cmake_args


    def get_arrow_cmake_args(self, arch):
        """
        Helper function to generate Arrow-specific CMake arguments.
        Does NOT include standard p4a args like toolchain or install prefix.
        These will be added manually in build_arch.
        """
        arrow_cmake_args = []

        # --- Arrow Feature Flags ---
        arrow_cmake_args.extend([
            '-DARROW_BUILD_TESTS=OFF',
            '-DARROW_BUILD_BENCHMARKS=OFF',
            '-DARROW_BUILD_EXAMPLES=OFF',
            '-DARROW_BUILD_UTILITIES=OFF',
            '-DARROW_PYTHON=OFF',
            '-DARROW_INSTALL_NAME_RPATH=OFF', # Usually OFF for cross-compiling

            # Disable complex/optional components
            '-DARROW_CUDA=OFF',
            '-DARROW_DATASET=OFF', # Keep minimal for now
            '-DARROW_FLIGHT=OFF',
            '-DARROW_GANDIVA=OFF',
            '-DARROW_HDFS=OFF',
            '-DARROW_ORC=OFF',
            '-DARROW_PARQUET=OFF',
            '-DARROW_SUBSTRAIT=OFF',
            '-DARROW_ACERO=OFF',
            '-DARROW_S3=OFF',
            '-DARROW_GCS=OFF',
            '-DARROW_AZURE=OFF',
            '-DARROW_JEMALLOC=OFF', # Avoid extra dependency
            '-DARROW_MIMALLOC=OFF', # Avoid extra dependency
        ])

        # Enable core components
        arrow_cmake_args.extend([
            '-DARROW_COMPUTE=ON',
            '-DARROW_FILESYSTEM=ON',
            '-DARROW_IPC=ON',
            '-DARROW_CSV=ON',
            '-DARROW_JSON=ON',
        ])

        # --- Dependency Handling ---
        # Explicitly prefer system libraries (from other recipes)
        #arrow_cmake_args.append('-DARROW_DEPENDENCY_SOURCE=SYSTEM')

        # Correctly format ON/OFF flags based on self.depends
        arrow_cmake_args.append(f'-DARROW_WITH_ZLIB={"ON" if "zlib" in self.depends else "OFF"}')
        arrow_cmake_args.append(f'-DARROW_WITH_LZ4={"ON" if "lz4" in self.depends else "OFF"}')
        arrow_cmake_args.append(f'-DARROW_WITH_ZSTD={"ON" if "zstd" in self.depends else "OFF"}')
        arrow_cmake_args.append(f'-DARROW_WITH_BROTLI={"ON" if "brotli" in self.depends else "OFF"}')
        arrow_cmake_args.append('-DARROW_WITH_SNAPPY=OFF') # Add 'snappy' to depends if needed
        arrow_cmake_args.append('-DARROW_WITH_BZ2=OFF')    # Add 'bz2' to depends if needed
        arrow_cmake_args.append('-DARROW_WITH_OPENSSL=OFF') # Add 'openssl' to depends if needed (e.g., for S3)
        arrow_cmake_args.append('-DARROW_WITH_BOOST=OFF') # Boost is heavy, avoid if possible

        # Use bundled for simple internal deps unless recipes exist and are preferred
        # Tarball usually includes these source files in cpp/thirdparty
        arrow_cmake_args.extend([
            '-DARROW_RE2_SOURCE=BUNDLED', # Use BUNDLED for source, but requires CMake target `re2::re2`
            '-DARROW_UTF8PROC_SOURCE=BUNDLED',
            '-DARROW_RAPIDJSON_SOURCE=BUNDLED',
            # Check Arrow CMake options for exact names, might be:
            # '-Dre2_SOURCE=BUNDLED', '-Dutf8proc_SOURCE=BUNDLED'
            # Simpler: Let Arrow handle finding/building bundled versions if SYSTEM fails
            # Or, explicitly force bundled (might be simpler for Android)
            # '-DARROW_WITH_RE2=BUNDLED', # Let's try forcing BUNDLED build logic
            # '-DARROW_WITH_UTF8PROC=BUNDLED',
            # Revert to AUTO to let it try system then bundled? No, SYSTEM should be preferred.
            # Let's rely on ARROW_DEPENDENCY_SOURCE=SYSTEM and see if Brotli works.
            # If Brotli fails again, consider forcing it to BUNDLED:
            # '-DARROW_WITH_BROTLI=BUNDLED' # Add this only if SYSTEM fails for Brotli
        ])

        # --- Build & Install Options ---
        arrow_cmake_args.extend([
            '-DCMAKE_INSTALL_LIBDIR=lib',      # Install to 'lib' not 'lib64'
            '-DARROW_SIMD_LEVEL=NONE',         # Disable SIMD for initial build simplicity
            '-DARROW_RUNTIME_SIMD_LEVEL=NONE',
            '-DARROW_USE_CCACHE=OFF',          # p4a handles caching if enabled globally
            '-DBUILD_SHARED_LIBS=ON',          # Build shared libraries (.so)
            '-DARROW_BUILD_STATIC=ON',        # Don't build static libs (.a)
            # '-DCMAKE_UNITY_BUILD=ON',        # Consider enabling later for faster builds
        ])

        # Add hints for Brotli if SYSTEM search fails (uncomment and adjust if needed)
        # brotli_recipe = Recipe.get_recipe('brotli', self.ctx)
        # brotli_install_dir = brotli_recipe.get_build_dir(arch.arch) # Or get_install_dir? Check brotli recipe
        # arrow_cmake_args.extend([
        #     f'-DBROTLI_ROOT={brotli_install_dir}',
        #     # Might need more specific hints depending on FindBrotliAlt.cmake
        #     # f'-DBROTLI_INCLUDE_DIRS={brotli_install_dir}/include',
        #     # f'-DBROTLI_COMMON_LIBRARY={brotli_install_dir}/lib/libbrotlicommon.so',
        #     # f'-DBROTLI_ENC_LIBRARY={brotli_install_dir}/lib/libbrotlienc.so',
        #     # f'-DBROTLI_DEC_LIBRARY={brotli_install_dir}/lib/libbrotlidec.so',
        # ])

        # --- 调试 ---
        info("--- Contents of arrow_cmake_args before return: ---")
        info(str(arrow_cmake_args))
        # --- 调试结束 ---
        return arrow_cmake_args




    def build_arch_v1(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_target = join(source_dir, 'build')
        install_target = join(build_target, 'install')

        ensure_dir(build_target)
        with current_directory(build_target):
            env = self.get_recipe_env(arch)
            ndk_dir = self.ctx.ndk_dir
            rmdir('CMakeFiles')
            shprint(sh.rm, '-f', 'CMakeCache.txt', _env=env)
            opts = [
                    '-DCMAKE_SYSTEM_NAME=Android',
                    '-DCMAKE_POSITION_INDEPENDENT_CODE=1',
                    '-DCMAKE_ANDROID_ARCH_ABI={arch}'.format(arch=arch.arch),
                    '-DCMAKE_ANDROID_NDK=' + ndk_dir,
                    '-DCMAKE_ANDROID_API={api}'.format(api=self.ctx.ndk_api),
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DCMAKE_INSTALL_PREFIX={}'.format(install_target),
                    '-DCBLAS=ON',
                    '-DBUILD_SHARED_LIBS=ON',
                    f'-DCMAKE_INSTALL_PREFIX={env["ARROW_HOME"]}',
                    '--preset ninja-release-python'
                    ]
            
            if arch.arch == 'armeabi-v7a':
                opts.append('-DCMAKE_ANDROID_ARM_NEON=ON')
                
            opts.extend(self.get_arrow_cmake_args(arch))
                
            shprint(sh.cmake, '-S', 'arrow/cpp', '-B', 'arrow/cpp/build', *opts, _env=env)
            
            shprint(sh.cmake, '--build', 'arrow/cpp/build', '--target', 'install', _env=env)
        

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch) # e.g., .../libarrow_cpp
        # 创建一个明确的构建目录，与源代码分开，这是推荐的做法
        build_dir_cmake = join(source_dir, 'p4a_build_cmake')

        # 定义实际的 C++ 源代码目录和 CMake 构建目录
        actual_source_dir_cpp = join(source_dir, 'cpp') # 确认的路径: .../libarrow_cpp/cpp
        actual_build_dir_cmake = build_dir_cmake      # 使用我们创建的目录: .../libarrow_cpp/p4a_build_cmake

        # --- 健壮性检查：确保源代码目录看起来是正确的 ---
        expected_cmakelists = os.path.join(actual_source_dir_cpp, 'CMakeLists.txt')
        if not os.path.exists(expected_cmakelists):
             # 如果找不到，也许下载/解压出了问题，或者路径假设错误
             raise BuildInterruptingException(
                 f"CMakeLists.txt not found in expected source directory: {actual_source_dir_cpp}. "
                 f"Checked path: {expected_cmakelists}"
             )

        ensure_dir(actual_build_dir_cmake) # 确保 CMake 构建目录存在
        
        
        
        

        # --- 在 CMake 构建目录中执行操作 ---
        with current_directory(actual_build_dir_cmake):
            env = self.get_recipe_env(arch)
            ndk_dir = self.ctx.ndk_dir
            ndk_api = self.ctx.ndk_api

            toolchain_file = join(ndk_dir, 'build', 'cmake', 'android.toolchain.cmake')
            ep_cmake_args = [
                f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                f"-DANDROID_ABI={arch.arch}",
                f"-DANDROID_PLATFORM=android-{ndk_api}",
                f"-DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>", # 这个会被 ExternalProject 覆盖，但有时需要占位
                f"-DCMAKE_BUILD_TYPE=Release",          # 与主构建保持一致
                # 可能需要添加 -DBUILD_SHARED_LIBS=OFF 如果 re2 默认构建共享库
                "-DBUILD_SHARED_LIBS=OFF",
            ]
            # 将列表连接成 CMake List 格式（分号分隔）
            ep_cmake_args_str = ";".join(ep_cmake_args)
            
            # 注意：当使用独立的构建目录时，通常不需要手动删除 CMakeCache.txt 或 CMakeFiles
            # 除非 CMake 参数发生了重大变化。p4a clean_recipe 是更可靠的清理方式。

            # --- CMake 配置参数 ---
            opts = [
                # 推荐使用 Android NDK 提供的 toolchain 文件来配置交叉编译环境
                '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                    join(ndk_dir, 'build', 'cmake', 'android.toolchain.cmake')),
                # 通过 toolchain 文件设置 ABI 和 API Level 通常更标准
                '-DANDROID_ABI={arch}'.format(arch=arch.arch),
                '-DANDROID_PLATFORM=android-{api}'.format(api=self.ctx.ndk_api),
                # '-DANDROID_NDK={}'.format(ndk_dir), # Toolchain 文件通常会处理 NDK 路径
                # '-DCMAKE_SYSTEM_NAME=Android', # Toolchain 文件会设置
                '-DCMAKE_BUILD_TYPE=Release', # 设置构建类型为 Release
                '-DCMAKE_INSTALL_PREFIX={}'.format(env["ARROW_HOME"]), # 设置安装路径，使用 env 中的 ARROW_HOME
                # '-DCMAKE_POSITION_INDEPENDENT_CODE=1', # 通常由 toolchain 自动处理共享库
                '-DBUILD_SHARED_LIBS=ON', # 明确构建共享库 (libarrow.so 等)
                # '--preset ninja-release-python' # 已移除，我们手动控制所有选项
                f'-DCMAKE_ARGS={ep_cmake_args_str}',
                '-DCMAKE_VERBOSE_MAKEFILE=ON',
            ]

            # 为特定架构添加特定标志 (例如 NEON for armeabi-v7a)
            # 注意：对于 arm64-v8a，NEON 通常是默认启用的，无需显式设置
            if arch.arch == 'armeabi-v7a':
                 opts.append('-DANDROID_ARM_NEON=ON') # NDK 中正确的标志名

            # 添加 Arrow 特定的编译选项 (来自 get_arrow_cmake_args 函数)
            opts.extend(self.get_arrow_cmake_args(arch))

            # 显式指定使用 Ninja 构建器（p4a 通常会确保 ninja 可用）
            ninja_path = sh.which('ninja')
            if ninja_path:
                opts.extend(['-G', 'Ninja'])
                info("Using Ninja generator for CMake.")
            else:
                self.warning("Ninja not found, CMake will use default generator (likely Makefiles).")
                # 如果没有 Ninja，可能需要移除 get_arrow_cmake_args 中可能存在的 Ninja 特定预设相关标志（虽然我们已经移除了preset）

            # --- 执行 CMake 配置步骤 ---
            # 使用 -S 指定源代码目录，-B 指定构建目录 (当前目录)
            info(f"Running CMake configuration in {actual_build_dir_cmake}")
            shprint(sh.cmake,
                    '-S', actual_source_dir_cpp,  # 绝对或相对正确的源代码路径
                    '-B', actual_build_dir_cmake, # 绝对或相对正确的构建目录路径
                    *opts,
                    _env=env)

            # --- 执行 CMake 构建和安装步骤 ---
            info(f"Running CMake build and install in {actual_build_dir_cmake}")
            # 使用 --build 指向构建目录
            shprint(sh.cmake, '--build', actual_build_dir_cmake, '--target', 'install', _env=env) # -j N 可以稍后添加



recipe = ArrowCppRecipe()
