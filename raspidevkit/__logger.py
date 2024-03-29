import logging
from logging import Logger, Handler


class MachineLogger(Logger):
    def __init__(self, name: str, enabled: bool) -> None:
        super().__init__(name)
        self.enabled = enabled



    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG) and self.enabled:
            super().debug(msg, *args, **kwargs)
            if kwargs.get('to_stdout', False):
                print(msg)



    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and self.enabled:
            super().info(msg, *args, **kwargs)
            if kwargs.get('to_stdout', False):
                print(msg)



    def warn(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARN) and self.enabled:
            super().warn(msg, *args, **kwargs)
            if kwargs.get('to_stdout', False):
                print(msg)



    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR) and self.enabled:
            super().error(msg, *args, **kwargs)
            if kwargs.get('to_stdout', False):
                print(msg)



    def addHandler(self, hdlr: Handler) -> None:
        if self.enabled:
            return super().addHandler(hdlr)
        