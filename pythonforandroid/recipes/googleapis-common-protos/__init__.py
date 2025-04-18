from pythonforandroid.recipe import Recipe
from pathlib import Path
import shutil
from os.path import join
from pythonforandroid.logger import info
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.util import (
    current_directory, ensure_dir,
    BuildInterruptingException, rmdir
)
import copy
import os

class WheelRecipe(Recipe):
    
    def download_file(self, url, target, cwd=None):
        info(f"[lius debug] url:{url}, target:{target}")
        #info(f"[lius debug] self.ctx.hostpython:{self.ctx.hostpython}")
        
        # 使用 pip 下载指定版本的 wheel 文件
        # venv/bin/pip download --no-deps --dest ./downloaded_wheels googleapis_common_protos==1.69.2
        
        package_path = join(self.ctx.packages_path, self.name)
        
        info(f"[lius debug] package_path:{package_path}")
        shprint(sh.bash, '-c', (
            "pip " +
            "download --no-deps --dest '{0}' {1}"
        ).format(package_path, "googleapis_common_protos==1.69.2"))
            
        pass
    
    def unpack(self, arch):
        info(f"[lius debug] arch:{arch}")
        package_path = join(self.ctx.packages_path, self.name)
        build_dir = self.get_build_dir(arch)
        filename = shprint(sh.basename, self.url).stdout[:-1].decode('utf-8')
        
        rmdir(build_dir)
        
        ensure_dir(build_dir)
        
        #unzip your_package-1.0.0-py3-none-any.whl -d ./my_unpacked_wheel
        with current_directory(package_path):
            shprint(sh.unzip, filename, '-d', build_dir)
        

    def build_arch(self, arch):
        install_dir = self.ctx.get_site_packages_dir(arch).replace("'", "'\"'\"'")
        build_dir = self.get_build_dir(arch.arch)
        info(f"[lius debug] install_dir:{install_dir}")
        info(f"[lius debug] build_dir:{build_dir}")
        
        # 获取build_dir目录下的所有文件和文件夹，不包括 . 和 ..
        files_and_dirs = [f for f in os.listdir(build_dir) if f not in ['.', '..']]
        
        ensure_dir(install_dir)
        # 遍历列表并复制每个文件或目录到安装目录
        for each_file_or_dir in files_and_dirs:
            source_path = join(build_dir, each_file_or_dir)
            info(f"[lius debug] copy: {source_path} to {install_dir}")
            shprint(sh.cp, "-rf", source_path, install_dir)
        
        


class GoogleapisCommonProtosRecipe(WheelRecipe):
    version = '1.69.2'
    #url = f'https://files.pythonhosted.org/packages/source/p/protobuf/protobuf-{version}.tar.gz'
    #url = f'https://files.pythonhosted.org/packages/source/g/googleapis_common_protos/googleapis_common_protos-{version}.tar.gz'
    url = f'https://files.pythonhosted.org/packages/googleapis_common_protos-{version}-py3-none-any.whl'
    name = "googleapis_common_protos"
    depends = ['protobuf']


recipe = GoogleapisCommonProtosRecipe()
