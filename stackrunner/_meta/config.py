import ast, _ast
import typing
import datetime
from dataclasses import dataclass

@dataclass
class Signature:
    arguments: typing.Union[int] #TODO strict definition
    type_: typing.Literal[_ast.FunctionDef, _ast.ClassDef] = _ast.FunctionDef
    returns: typing.Optional[bool] = None
    strict: bool = False

    def compatable(self, definition: typing.Union[_ast.FunctionDef, _ast.ClassDef]) -> bool:
        if isinstance(definition, self.type_):
            if isinstance(self.arguments, int):
                # Has the right number of arguments
                if self.type_ is _ast.ClassDef:

                    try:
                        definition = next(func for func in definition.body if func.name == '__init__')
                    except StopIteration:
                        return False
                return len(definition.args.args) == self.arguments \
                        or len(definition.args.args) - len(definition.args.defaults) == self.arguments

        # TODO strict support
        # else:
        #     ...
        return False


safety_date = datetime.datetime(2020, 10, 17)
@dataclass
class RunnerConfig:
    tags: typing.List[str]
    not_tags: typing.List[str]
    signature: Signature
    parser: typing.Optional[typing.Callable[[str], ast.Module]] = None
    compiler: typing.Optional[typing.Callable[[str, 'RunnerConfig'], typing.Tuple[ast.Module, 'code']]] = None
    runner: typing.Optional[typing.Callable[[ast.Module, 'code', 'RunnerConfig'], typing.Callable]] = None
    safety_date: datetime.datetime = safety_date
    prefix: str = ''
