from pythonforandroid.recipe import RustCompiledComponentsRecipe, PyProjectRecipe, NDKRecipe, Recipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint
import sh
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
from pythonforandroid.logger import (
    logger, info, warning, debug, shprint, info_main, error)


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



class Python3LinkDepRecipe(Recipe):
    version = '1.0.0'
    url = f'https://example.com/python3_link_dep.tar.gz'
    depends = ['python3']
    name = 'python3_link_dep'

    def download_if_necessary(self):
        info_main('Downloading {}'.format(self.name))
        
        recipe_package_path = join(self.ctx.packages_path, self.name)
        ensure_dir(recipe_package_path)
        
        # 创建一个占位文件，用于满足下载需求
        placeholder_file = join(recipe_package_path, 'python3_link_dep.tar.gz')
        
        if exists(placeholder_file):
            info(f"删除占位文件: {placeholder_file}")
            shprint(sh.rm, '-f', placeholder_file)
        
        
        if not exists(placeholder_file):
            info(f"创建占位文件: {placeholder_file}")
            # 创建一个临时目录来准备tar.gz文件
            temp_dir = join(recipe_package_path, 'temp')
            ensure_dir(temp_dir)
            
            # 创建与recipe同名的目录
            recipe_dir = join(temp_dir, self.name)
            ensure_dir(recipe_dir)
            
            # 创建readme文件在recipe目录内
            readme_path = join(recipe_dir, 'readme.txt')
            with open(readme_path, 'w') as f:
                f.write("这是一个占位文件，没有实际作用，只用来在python3 recipe构建后，在ndk sysroot目录下创建相关的软连接。")
            
            # 创建tar.gz文件
            with current_directory(temp_dir):
                shprint(sh.tar, 'czf', placeholder_file, self.name)
            
            # 清理临时目录
            shprint(sh.rm, '-rf', temp_dir)
            
            info(f"占位文件创建完成: {placeholder_file}")
        else:
            info(f"占位文件已存在: {placeholder_file}")

    # TODO: delete when debug finish
    def should_build(self, arch):
        return True

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
            
            ndk_dir = self.ctx.ndk_dir

            print(f"lius debug log : ndk_dir = {ndk_dir}")
            print(shprint(sh.Command('chmod'), '+x', f'{python_link_root}/python-config'))
            ensure_file_link(f'{python_link_root}/python-config', f'{python_build_dir}/python{python_link_version}-config')
            ensure_file_link(f'/home', f'{ndk_dir}/toolchains/llvm/prebuilt/linux-x86_64/sysroot/home')
            ensure_file_link(f'{python_include_root}', f'{python_build_dir}/include')
            

recipe = Python3LinkDepRecipe()
