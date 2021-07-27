
from cognate import ComponentCore

class Observer(ComponentCore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def cognate_options(self, arg_parser):
        pass

    def cognate_configure(self, args):
        pass
