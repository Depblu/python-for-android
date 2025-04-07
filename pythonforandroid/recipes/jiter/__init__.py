from pythonforandroid.recipe import RustCompiledComponentsRecipe
from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split

class JiterRecipe(RustCompiledComponentsRecipe):
    version = '0.9.0'
    url = f'https://github.com/pydantic/jiter/archive/refs/tags/v{version}.tar.gz'
    depends = []
    #hostpython_prerequisites = ['setuptools', 'wheel']
    site_packages_name = 'jiter'

    def get_build_dir_step_build(self, arch):
        base_dir = join(self.get_build_container_dir(arch), self.name)
        return join(base_dir, 'crates', 'jiter-python')
    
    def build_arch(self, arch):
        import copy
        # 深度拷贝get_build_dir方法进行备份
        original_get_build_dir = copy.deepcopy(self.__class__.get_build_dir)
        # 将get_build_dir方法替换为get_build_dir_step_build方法
        self.__class__.get_build_dir = self.__class__.get_build_dir_step_build
        
        try:
            # 调用父类的build_arch方法
            super().build_arch(arch)
        finally:
            # 还原原来的get_build_dir方法
            self.__class__.get_build_dir = original_get_build_dir
        
        

recipe = JiterRecipe()
