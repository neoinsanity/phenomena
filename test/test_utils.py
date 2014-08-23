from io import StringIO
import sys


class StdOutCapture(list):
    def __init__(self, seq=(), noop=False):
        super(StdOutCapture, self).__init__(seq)

        self._noop = noop

    def __enter__(self):
        if self._noop:
            return self

        self._original_stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._noop:
            return

        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._original_stdout
