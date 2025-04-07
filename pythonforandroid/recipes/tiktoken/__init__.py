from pythonforandroid.recipe import RustCompiledComponentsRecipe


class TiktokenRecipe(RustCompiledComponentsRecipe):
    name = 'tiktoken'
    version = '0.9.0'
    url = 'https://github.com/openai/tiktoken/archive/refs/tags/{version}.tar.gz'
    sha512sum = "953867bef8e2e9309d81ae38c54c5324e8a82efa379e56903cb7fae14c3700cd3d15a84a0ecb68be0f61cff2f7e84d99d2a4de18cf9bd0ba0a5c94ef76952630"
    depends = ['regex', 'requests']


recipe = TiktokenRecipe()
