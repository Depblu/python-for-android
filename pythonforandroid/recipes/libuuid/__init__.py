from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
import sh
from packaging import version as packaging_version


class LibuuidRecipe(Recipe):
    version = '1.0.0'
    url = 'https://github.com/cloudbase/libuuid/archive/refs/heads/master.zip'
    depends = []
    patches = ['flock_fix.patch']
    
    

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        
        print("////////// env export commands:")
        for key, value in env.items():
            print(f"export {key}='{value}'")
        print("/////////////")
        
        with current_directory(self.get_build_dir(arch.arch)):
            bash = sh.Command('bash')
            shprint(
                bash,
                'configure',
                '--host={}'.format(arch.command_prefix),
                '--disable-shared',
                _env=env,
            )
            shprint(sh.make, _env=env)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # 设置基本NDK环境变量
        env['NDK_HOME'] = self.ctx.ndk_dir
        env['TOOLCHAIN'] = env['NDK_HOME'] + '/toolchains/llvm/prebuilt/linux-x86_64'
        env['API'] = '26'
        env['TARGET'] = 'aarch64-linux-android' + env['API']
        env['SYSROOT'] = env['TOOLCHAIN'] + '/sysroot'
        
        # 设置PATH以包含工具链路径
        env['PATH'] = env['TOOLCHAIN'] + '/bin:' + env['PATH']
        
        # 设置交叉编译工具
        env['CC'] = 'clang'
        env['CXX'] = 'clang++'
        env['AR'] = 'llvm-ar'
        env['AS'] = 'llvm-as'
        env['LD'] = 'ld.lld'
        env['RANLIB'] = 'llvm-ranlib'
        env['STRIP'] = 'llvm-strip'
        
        # 设置编译和链接标志
        target_flags = '--target=' + env['TARGET'] + ' --sysroot=' + env['SYSROOT']
        arch_flags = '-fPIC -march=armv8-a -fomit-frame-pointer'
        env['CFLAGS'] = target_flags + ' ' + arch_flags
        env['CXXFLAGS'] = target_flags + ' ' + arch_flags
        env['LDFLAGS'] = target_flags
        
        
        env['CFLAGS'] += ' -Os'
        return env


recipe = LibuuidRecipe()
