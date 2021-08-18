from io import StringIO
import os
import sys

from gevent import sleep, spawn


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


def spawn_observer(observer_class=None, argv=None):
    assert observer_class
    observer = observer_class(argv=argv)
    the_spawn = spawn(observer.run)
    sleep(0)  # yield so the spawn can execute.

    return the_spawn, observer


def gen_archive(test_name=None):
    assert test_name
    return _gen_test_path('archive', test_name + '.archive')


def gen_concept(test_name=None):
    assert test_name
    return _gen_test_path('concept', test_name + '.concept')


def gen_input(test_name=None):
    assert test_name
    return _gen_test_path('input', test_name + '.input')


def gen_output(test_name=None):
    assert test_name
    return _gen_test_path('output', test_name + '.output')


def gen_archive_input_output_triad(test_name=None):
    return gen_archive(test_name), gen_input(test_name), gen_output(test_name)


def gen_archive_output_concept_triad(test_name=None):
    return gen_archive(test_name), gen_output(test_name), gen_concept(test_name)


def gen_input_output_pair(test_name=None):
    return gen_input(test_name), gen_output(test_name)


def gen_input_output_blueprint_triad(test_name=None):
    return gen_input(test_name), gen_output(test_name), gen_concept(test_name)


def _gen_test_path(folder=None, file_name=None):
    return os.path.join('test_data', folder, file_name)
