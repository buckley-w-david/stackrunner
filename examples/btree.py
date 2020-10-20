import ast, _ast
import stackrunner
# Handle imports to stackrunner.sort

from stackrunner._meta.compiler import refactor2to3, clean_top_level


def custom_parse(code: str) -> ast.Module:
    try:
        code = refactor2to3(code)
    except Exception:
        pass

    tree = ast.parse(code)
    clean_top_level(tree)
    return tree

btree_config = stackrunner.RunnerConfig(
    tags=["python", "search", "data-structures", "binary-tree"],
    not_tags=["python-2.x"],
    signature=stackrunner.Signature(
        arguments=1,
        type_=_ast.ClassDef
    ),
    parser=custom_parse,
    prefix='btree'
)

import logging
stackrunner.logger.setLevel(level=logging.DEBUG)
logging.basicConfig()
stackrunner.init(btree_config)

from stackrunner.btree import binary_tree as BTree

tree = BTree()
