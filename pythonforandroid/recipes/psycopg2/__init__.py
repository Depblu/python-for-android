from pythonforandroid.recipe import PythonRecipe, Recipe
from pythonforandroid.toolchain import current_directory, shprint
import sh
from pythonforandroid.logger import shprint, info
import os


class Psycopg2Recipe(PythonRecipe):
    """
    Requires `libpq-dev` system dependency e.g. for `pg_config` binary.
    If you get `nl_langinfo` symbol runtime error, make sure you're running on
    `ANDROID_API` (`ndk-api`) >= 26, see:
    https://github.com/kivy/python-for-android/issues/1711#issuecomment-465747557
    """
    version = '2.8.5'
    url = 'https://pypi.python.org/packages/source/p/psycopg2/psycopg2-{version}.tar.gz'
    depends = ['libpq', 'setuptools']
    site_packages_name = 'psycopg2'
    call_hostpython_via_targetpython = False

    def prebuild_arch(self, arch):
        libpq_version = Recipe.get_recipe("libpq", self.ctx).version
        libdir = self.ctx.get_libs_dir(arch.arch)
        build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
            # pg_config_helper will return the system installed libpq, but we
            # need the one we just cross-compiled
            # shprint(sh.sed, '-i',
            #         "s|pg_config_helper.query(.libdir.)|'{}'|".format(libdir),
            #         'setup.py')
            

            # 创建一个假的 pg_config 脚本
            fake_pg_config_path = os.path.join(build_dir, 'pg_config')
            with open(fake_pg_config_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write('case "$1" in\n')
                # 根据 setup.py 的调用情况，返回所需的值
                # 注意：这些路径需要基于 get_recipe_env 中设置的环境变量或硬编码
                f.write(f'  --includedir) echo "{build_dir}";;\n')
                f.write(f'  --includedir-server) echo "{build_dir}";;\n') # 假设服务器头文件也在同一位置
                f.write(f'  --libdir) echo "{self.ctx.get_libs_dir(arch.arch)}";;\n')
                f.write('  --ldflags) echo "$LDFLAGS";;\n') # 提供基本的 LDFLAGS
                f.write('  --cppflags) echo "$CPPFLAGS";;\n') # 提供基本的 CPPFLAGS
                f.write(f'  --version) echo "PostgreSQL {libpq_version}";;\n') # 提供基本的 version
                f.write('  *) echo "Unsupported pg_config option: $1"; exit 1;;\n')
                f.write('esac\n')
                f.write('exit 0\n')

            # 赋予执行权限
            os.chmod(fake_pg_config_path, 0o755)
            


    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['LDFLAGS'] = "{} -L{}".format(env['LDFLAGS'], self.ctx.get_libs_dir(arch.arch))
        env['EXTRA_CFLAGS'] = "--host linux-armv"
        
        libdir = self.ctx.get_libs_dir(arch.arch)
        libpq_build_dir = Recipe.get_recipe("libpq", self.ctx).get_build_dir(arch.arch)
        #include dir
        #'''
        #/home/lius/.local/share/python-for-android/build/other_builds/libpq/arm64-v8a__ndk_target_26/libpq/src/interfaces/libpq
        #/home/lius/.local/share/python-for-android/build/other_builds/libpq/arm64-v8a__ndk_target_26/libpq/src/include
        #'''

        # 将依赖项的库和头文件路径添加到 LDFLAGS 和 CFLAGS
        #env['LDFLAGS'] = env.get('LDFLAGS', '') + f' -L{libdir}'
        env['CPPFLAGS'] = env.get('CPPFLAGS', '') + f' -I{libpq_build_dir}/src/interfaces/libpq -I{libpq_build_dir}/src/include'
        # 如果需要，可以添加 RPATH 等
        #env['LDFLAGS'] += f' -Wl,-O1 -Wl,--sort-common -Wl,--as-needed -Wl,-z,relro -Wl,-z,now -Wl,-z,pack-relative-relocs -flto=auto -Wl,--as-needed'


        info(f"psycopg2 CFLAGS: {env['CPPFLAGS']}")
        info(f"psycopg2 LDFLAGS: {env['LDFLAGS']}")
        return env


    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        '''Automate the installation of a Python package (or a cython
        package where the cython components are pre-built).'''
        if env is None:
            env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'build_ext', '--static-libpq', '--pg-config', './pg_config',
                    _env=env)
            shprint(hostpython, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                    '--install-lib=.', _env=env)


recipe = Psycopg2Recipe()
