import ast, _ast
import copy
import functools
import types

from stackrunner._meta import errors

def entrypoints(tree: _ast.Module, signature):
    return [
        f.name
        for f in tree.body
        if isinstance(f, _ast.FunctionDef) and signature.compatable(f)
    ]

# https://stackoverflow.com/a/49077211
'''
This function returns a copy of a given function, but with
it's __globals__ switched out.

This is used so that we can exec the compiled module without polluting the global scope
while allowing references to still be accessed from within the defined functions
'''
def copy_func(f, globals=None, module=None):
    """Based on https://stackoverflow.com/a/13503277/2988730 (@unutbu)"""
    if globals is None:
        globals = f.__globals__
    g = types.FunctionType(f.__code__, globals, name=f.__name__,
                           argdefs=f.__defaults__, closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    if module is not None:
        g.__module__ = module
    g.__kwdefaults__ = copy.copy(f.__kwdefaults__)
    return g

class ReplaceGlobals(ast.NodeTransformer):
    def __init__(self, globals):
        self.globals = globals

    def visit_FunctionDef(self, node):
        if isinstance(node, _ast.FunctionDef):
            func = self.globals[node.name]
            self.globals[node.name] = copy_func(func, self.globals)

        return node

class CodeBlockRunner:
    def __init__(self, tree, compiled_module, config):
        self.tree = tree
        self.code = compiled_module
        self.working_entrypoint = None
        self.err = errors.MultiError()
        self._config = config

        self.locals = {}
        self.globals = {}
        exec(compiled_module, self.globals, self.locals)

        # Repalce __globals__ on all functions
        self.combined_scope = {**self.globals, **self.locals}
        fixer = ReplaceGlobals(self.combined_scope)
        fixer.visit(tree)

    def __call__(self, *args, **kwargs):
        if self.working_entrypoint:
            return self.working_entrypoint(*args, **kwargs)

        sig = self._config.signature

        for entrypoint in entrypoints(self.tree, sig):
            try:
                func = self.combined_scope[entrypoint]
                val = func(*args, **kwargs)
                if sig.returns is None or sig.returns and val:
                    self.working_entrypoint = func
                    return val
                elif not sig.returns and not val:
                    self.working_entrypoint = func
                    return
            except Exception as e:
                self.err.add_context(e)

        raise errors.NoValidCodeError("Code block contains no working entrypoints that match the signature") from self.err
