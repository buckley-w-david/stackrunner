import ast, _ast
import typing

from stackrunner._meta import errors

# Never thought I'd import this... What a world we live in
from lib2to3 import refactor
fixers = refactor.get_fixers_from_package('lib2to3.fixes') # Why is this package like this?
refactoring_tool = refactor.RefactoringTool(fixers)

class RemovePrints(ast.NodeTransformer):
    def visit_Expr(self, node):
        if isinstance(node, _ast.Expr) \
                and isinstance(node.value, _ast.Call) \
                and isinstance(node.value.func, _ast.Name) \
                and node.value.func.id == 'print':
            return ast.Pass() # replace prints with noop
        return node

print_remover = RemovePrints()
def remove_prints(tree: ast.AST) -> ast.AST:
    return print_remover.visit(tree)

def refactor2to3(code: str) -> str:
    return str(refactoring_tool.refactor_string(code, 'StackOverflow'))

def clean_top_level(tree: ast.Module) -> ast.AST:
    tree.body = [
        node for node in tree.body
        if isinstance(node, _ast.FunctionDef) \
        or isinstance(node, _ast.ClassDef) \
        or isinstance(node, _ast.Import) \
        or isinstance(node, _ast.ImportFrom)
    ]

def parse(code: str) -> ast.Module:
    try:
        code = refactor2to3(code)
    except Exception:
        pass

    tree = remove_prints(ast.parse(code))
    clean_top_level(tree)
    return tree

def compile_block(code_block, config) -> typing.Tuple[ast.AST, 'code']:
    if config.parser:
        parse = config.parser
    try:
        tree = parse(code_block)
        if not any(isinstance(node, config.signature.type_) for node in tree.body):
            raise errors.NoValidCodeError(f"Caller must provide a custom compiler to handle blocks that do not define any {config.signature.type_}")

        compiled_code = compile(ast.fix_missing_locations(tree), '<StackOverflow>', 'exec')
    except Exception as exc:
        raise errors.NoValidCodeError("Unable to compile code block") from exc

    return (tree, compiled_code)

#
#         # If the code does not define any functions
#         if not any(isinstance(node, _ast.FunctionDef) for node in new_tree.body):
#             # Determine paramater name
#             #
#             # SCRAPPED - Getting a list of names referenced is easy, but figuring out which of them
#             # are unitialized is impossible. You can hack it to probably get most of the way there
#             # but technically it can be done completely dynamically via strings and such.
#             #
#             # Scan for usages of variables that have not been declared -
#             #  - If there is 1, you have found your paramater name
#             #  - If there are 0, look for a variable that was initialized to a list
#             #  - If there are more than 1, abort probably
#             #
#             # -----------------------------------------
#             #
#             # At least for now, we're gonna be lazy
#             # Any top level lists created that are not empty = our paramater
#             # Otherwise, we give up.
#             #
#             # Figure out what to return
#             #  - If there is a variable initialized to an empty list, return that
#             #  - else, return the function paramater (assume in-place sort)
#
#             return_name = None
#             param_name = None
#
#             for node in new_tree.body:
#                 if isinstance(node, _ast.Assign):
#                     if isinstance(node.value, _ast.List):
#                         if len(node.value.elts):
#                             param_name = node.targets[0].id
#                         else:
#                             return_name = node.targets[0].id
#             return_name = return_name or param_name
#
#             if not param_name:
#                 raise NoValidCodeError("¯\_(ツ)_/¯")
#
#             # Yeet assignments to the paramater found in first section
#             yeeter = RemoveAssigns(param_name)
#             newer_tree = yeeter.visit(new_tree)
#
#             # Wrap the code in a function called sort
#             # Man, how did I get to the point in my life where I'm manually writing ASTs?
#             sort_func = ast.FunctionDef(
#                 name='sort',
#                 args=ast.arguments(
#                     posonlyargs=[],
#                     args=[
#                         ast.arg(
#                             arg=param_name,
#                             annotation=None,
#                             type_comment=None
#                         )
#                     ],
#                     vararg=None,
#                     kwonlyargs=[],
#                     kw_defaults=[],
#                     kwarg=None,
#                     defaults=[]
#                 ),
#                 body=[
#                     *newer_tree.body,
#                     ast.Return(
#                         value=ast.Name(
#                             id=return_name,
#                             ctx=ast.Load()
#                         )
#                     )
#                 ],
#                 decorator_list=[],
#                 returns=None,
#                 type_comment=None
#             )
#             new_tree.body = [sort_func]

# Extracted from stacksort
# TODO remove
# class MultipleError(Exception):
#     def __init__(self, context=None):
#         self.context = [] if context is None else context
#
#     def add_context(self, context: Exception):
#         self.context.append(context)
#
#     @property
#     def message(self):
#         return '\n'.join(str(exc) for exc in self.context)
#
# def valid_signature(func_def: _ast.FunctionDef):
#     # Only 1 function argument, or only 1 that isn't given a default value
#     return len(func_def.args.args) == 1 or len(func_def.args.args) - len(func_def.args.defaults) == 1
#
# def entrypoints(tree: _ast.Module):
#     return [
#         f.name
#         for f in tree.body
#         if isinstance(f, _ast.FunctionDef) and valid_signature(f)
#     ]
#
#
# class RemoveAssigns(ast.NodeTransformer):
#     def __init__(self, name, *args, **kwargs):
#         self.__yeet = name
#         super().__init__(*args, **kwargs)
#
#     def visit_Assign(self, node):
#         if isinstance(node.targets[0], _ast.Name) and node.targets[0].id == self.__yeet:
#             return None
#         return node
#
#
# remove_prints = RemovePrints()
#
