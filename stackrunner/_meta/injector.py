import importlib.abc
import importlib.machinery
import sys
import types

import logging
logger = logging.getLogger(__name__)

from stackrunner._meta import compiler
from stackrunner._meta import stackoverflow
from stackrunner._meta import runner
from stackrunner._meta import errors

__name_parts =  __name__.split('.')
if __name_parts:
    _COMMON_PREFIX = __name_parts[0]
else:
    _COMMON_PREFIX = __name__

class Runner():
    def __init__(self, name, config):
        self._name = name
        self._config = config
        self._working_runner = None
        self._blocks = None

        if not config.compiler:
            self._compiler = compiler.compile_block
        else:
            self._compiler = config.compiler

        if not config.runner:
            self._runner = runner.CodeBlockRunner
        else:
            self._runner = config.runner

    def __call__(self, *args, **kwargs):
        if self._working_runner:
            return self._working_runner(*args, **kwargs)

        if not self._blocks:
            self._blocks = stackoverflow.fetch_code(self._name.replace('_', ' '), self._config)

        for code_block in self._blocks:
            logger.debug('CODE BLOCK\n\n%s\n\n', code_block)
            try:
                ast, compiled = self._compiler(code_block, self._config)
                block_runner = self._runner(ast, compiled, self._config)
                rval = block_runner(*args, **kwargs)
                self._working_runner = block_runner
                return rval
            except Exception as e:
                logger.debug(e)
        raise errors.NoValidCodeError("No valid code blocks")

    def __next__(self):
        self._working_runner = None
        return self

'''
Allows "namespace" import functionality, like so


    from stackrunner.stacksort import quicksort

    import stackrunner.stacksort
    stacksort.quicksort(...)


With each namespace having its own config (And so their own way to search/compile code)
'''
class RunnerModule():
    __path__ = 'stackrunner'

    def __init__(self, config):
        self._config = config

    def __call__(self, query):
        return Runner(query, self._config)

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError()
        return Runner(name, self._config)


class StackRunnerFinder(importlib.abc.MetaPathFinder):
    def __init__(self, loader, config):
        self._loader = loader
        self._config = config

    def find_spec(self, fullname, path, target=None):
        config = self._config

        if config.prefix == '':
            if fullname.startswith(f"{_COMMON_PREFIX}."):
                return self._gen_spec(fullname)
            return

        if fullname.startswith(f"{_COMMON_PREFIX}.{config.prefix}"):
            return self._gen_spec(fullname)

    def _gen_spec(self, fullname):
        return importlib.machinery.ModuleSpec(fullname, self._loader)

    def inject(self):
        sys.meta_path.append(self)

class StackRunnerLoader(importlib.abc.Loader):
    def __init__(self, config):
        self._config = config

    def create_module(self, spec):
        fullname = spec.name
        config = self._config

        if config.prefix == '':
            if fullname.startswith(f"{_COMMON_PREFIX}."):
                name = fullname[len(f"{_COMMON_PREFIX}."):]
                return Runner(name, config)
            return

        if fullname.startswith(f"{_COMMON_PREFIX}.{config.prefix}"):
            return RunnerModule(config)

    def exec_module(self, module):
        pass
