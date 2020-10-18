class StackRunnerError(Exception):
    pass

class NoValidCodeError(StackRunnerError):
    pass

class MultiError(StackRunnerError):
    def __init__(self, context=None):
        self.context = [context] if context is not None else []

    def add_context(self, context: Exception):
        self.context.append(context)

    @property
    def message(self):
        return '\n'.join(str(exc) for exc in self.context)

