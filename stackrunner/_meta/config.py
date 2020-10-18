import ast, _ast
import typing
import datetime
from dataclasses import dataclass

@dataclass
class Signature:
    arguments: typing.Union[int] #TODO strict definition
    returns: typing.Optional[bool] = None
    strict: bool = False

    def compatable(self, func_def: _ast.FunctionDef) -> bool:
        if isinstance(self.arguments, int):
            # Has the right number of arguments
            return len(func_def.args.args) == self.arguments \
                    or len(func_def.args.args) - len(func_def.args.defaults) == self.arguments
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
    safety_date: datetime.datetime = safety_date
    prefix: str = ''


