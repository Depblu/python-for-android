from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pathlib import Path
import shutil
from os.path import join
from pythonforandroid.logger import info


class ProtobufRecipe(CompiledComponentsPythonRecipe):
    version = '5.29.4'
    url = f'https://files.pythonhosted.org/packages/source/p/protobuf/protobuf-{version}.tar.gz'
    stl_lib_name = "c++_shared"
    #hostpython_prerequisites = ["setuptools","pip"]

    depends = ['python3']
    site_packages_name = 'protobuf'
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        
        return env

    def build_arch(self, arch):
        super().build_arch(arch)



recipe = ProtobufRecipe()
