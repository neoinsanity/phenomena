
import unittest

from gevent import spawn

from phenomena.event_core import EventCore

class EventCoreTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_event_core(self):
        core = EventCore()

        self.assertIsNotNone(core)

        the_spawn = spawn(core.run)
        print the_spawn._exception

        core.kill()
