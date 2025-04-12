from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe, Recipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
import sh
from pythonforandroid.logger import shprint

class chromahnswlibRecipe(PyProjectRecipe):
    version = '1.0.0'
    url = f'https://github.com/chroma-core/chroma/archive/refs/tags/{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'chroma-hnswlib'
    RUST_ARCH_CODES = {
        "arm64-v8a": "aarch64-linux-android",
        "armeabi-v7a": "armv7-linux-androideabi",
        "x86_64": "x86_64-linux-android",
        "x86": "i686-linux-android",
    }
    
    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["http_proxy"] = "http://127.0.0.1:7890"
        env["https_proxy"] = "http://127.0.0.1:7890"
        env["HTTP_PROXY"] = "http://127.0.0.1:7890"
        env["HTTPS_PROXY"] = "http://127.0.0.1:7890"
        
        
        # add code block to Set rust build target
        build_target = self.RUST_ARCH_CODES[arch.arch]
        cargo_linker_name = "CARGO_TARGET_{}_LINKER".format(
            build_target.upper().replace("-", "_")
        )
        env["CARGO_BUILD_TARGET"] = build_target
        env[cargo_linker_name] = join(
            self.ctx.ndk.llvm_prebuilt_dir,
            "bin",
            "{}{}-clang".format(
                # NDK's Clang format
                build_target.replace("7", "7a")
                if build_target.startswith("armv7")
                else build_target,
                self.ctx.ndk_api,
            ),
        )
        
        #2. SQLite 链接错误
        #原因：“Compiling sqlx-macros”出现两次，一次编译目标是android一次是hostx86, 但“Compiling libsqlite3-sys”只出现一次。而sqlx-macros是依赖libsqlite3-sys的。
        #解决sqlx-macros链接错误，添加以下两个环境变量，其中x86_64_unknown_linux_gnu，可以通过执行`rustc -vV | grep host`来获得。
        # env["CC_x86_64_unknown_linux_gnu"] = "/usr/bin/cc"
        # env["AR_x86_64_unknown_linux_gnu"] = "/usr/bin/ar"
        # 
        rustc_cmd = sh.Command("rustc")
        rustc_cmd_output = rustc_cmd("-vV")
        # 提取包含'host'的行
        host_triple = None
        for line in rustc_cmd_output.splitlines():
            if 'host' in line:
                # "host: x86_64-unknown-linux-gnu"
                host_triple = line.split(":")[1].strip()
                break
        
        print(f"Rust host: {host_triple}")
        env[f"CC_{host_triple.replace('-', '_')}"] = "/usr/bin/cc"
        env[f"AR_{host_triple.replace('-', '_')}"] = "/usr/bin/ar"
        env[f"CFLAGS_{host_triple.replace('-', '_')}"] = ""
        
        
        #4. Python 库链接错误 (**-lpython3.9**** vs ****-lpython3.11****):** Pyo3 错误地检测或默认需要链接 Python 3.9，而 P4A 环境提供的是 Python 3.11
        python_recipe = Recipe.get_recipe("python3", self.ctx)
        build_dir = join(python_recipe.get_build_dir(arch), "android-build")
        full_version = python_recipe.version
        version_parts = full_version.split('.')
        python_version = ''
        if len(version_parts) >= 2:
            python_version = f"{version_parts[0]}.{version_parts[1]}"
            print(f"Setting PYO3_CROSS_PYTHON_VERSION to {python_version}")
        else:
            raise ValueError("Unexpected python version format, expected format like 3.11.5")
        
        env['PYO3_CROSS_PYTHON_VERSION'] = python_version
        env['PYO3_CROSS_LIB_DIR'] = build_dir
        
        return env
    
    
    def build_arch(self, arch):
        """
        3. arboard 编译错误 (不支持 Android):** 发现构建过程中试图编译 arboard，而它不支持 Android。
           根源: python_bindings 这个库依赖了 chroma-cli 这个命令行工具, chroma-cli 依赖 arboard。
           解决方案: 从 python_bindings/Cargo.toml 移除了对 chroma-cli 的依赖，并在 bindings.rs 中移除了所有对 cli 函数的引用和注册。
        """
        build_dir = self.get_build_dir(arch.arch)
        bindings_rs_path = join(build_dir, 'rust', 'python_bindings', 'src', 'bindings.rs')
        cargo_toml_path = join(build_dir, 'rust', 'python_bindings', 'Cargo.toml')

        print(f"Patching {bindings_rs_path} for Android build...")

        # 注释掉 use chroma_cli::chroma_cli;
        # 使用 try: except: 保证即使 sed 失败或文件不存在也能继续，避免中断构建
        try:
            shprint(sh.Command('sed'),
                '-i',
                r's|^use chroma_cli::chroma_cli;|\/\/ use chroma_cli::chroma_cli;|',
                bindings_rs_path
            )
            print("Commented out 'use chroma_cli::chroma_cli;'")
        except sh.ErrorReturnCode_1: # sed 找不到文件或模式时可能返回1
            print(f"Failed to comment out 'use chroma_cli::chroma_cli;' in {bindings_rs_path}. File or line might not exist.")
        except Exception as e:
            print(f"An unexpected error occurred while patching 'use': {e}")


        # 注释掉函数体内的 chroma_cli(args);
        # (\s* 匹配前面的空格)
        try:
            shprint(sh.Command('sed'),
                '-i',
                r's|^\s*chroma_cli(args);|\/\/ chroma_cli(args);|',
                bindings_rs_path
            )
            print("Commented out 'chroma_cli(args);' call")
        except sh.ErrorReturnCode_1:
            print(f"Failed to comment out 'chroma_cli(args);' in {bindings_rs_path}. File or line might not exist.")
        except Exception as e:
            print(f"An unexpected error occurred while patching call: {e}")
            
        #注释 rust/python_bindings/Cargo.toml中的'chroma-cli = { workspace = true }'
        try:
            shprint(sh.Command('sed'), '-i', r's|^chroma-cli = { workspace = true }|# chroma-cli = { workspace = true }|', cargo_toml_path)
            print("Commented out 'chroma-cli = { workspace = true }' in Cargo.toml")
        except sh.ErrorReturnCode_1:
            print(f"Failed to comment out 'chroma-cli =' in {cargo_toml_path}. File or line might not exist.")
        except Exception as e:
            print(f"An unexpected error occurred while patching Cargo.toml: {e}")

        # 调用父类的 build_arch 执行标准的 maturin 构建流程
        super().build_arch(arch)

recipe = chromahnswlibRecipe()
