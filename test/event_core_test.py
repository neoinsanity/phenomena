import unittest

from gevent import sleep, spawn

from phenomena.event_core import EventCore

class EventCoreTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_event_core(self):

        # test subject
        core = EventCore(log_level='info', verbose=True)
        #core = EventCore()
        self.assertIsNotNone(core)

        # test initial state
        self.assertTrue(core._stopped)

        # text run state
        the_spawn = spawn(core.run)
        sleep(0) # give the spawn a change to initialize
        self.assertFalse(core._stopped)

        # test shutdown state
        core.kill()
        #sleep(1) # yield to allow message propagation
        the_spawn.join()
        self.assertTrue(core._stopped)
