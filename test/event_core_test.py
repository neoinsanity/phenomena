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
        core = EventCore()
        self.assertIsNotNone(core)

        # test initial state
        self.assertTrue(core._stopped)

        # text run state
        the_spawn = spawn(core.run)
        sleep(0.005)  # give the spawn a change to initialize
        self.assertFalse(core.is_stopped)

        # test shutdown state
        core.kill()
        # sleep(1) # yield to allow message propagation
        the_spawn.join(timeout=5)
        self.assertTrue(core.is_stopped)

    def test_event_core_restart(self):
        # test subject
        core = EventCore(command_port=9901)
        self.assertIsNotNone(core)

        # start and shutdown in prep for restart
        the_spawn = spawn(core.run)
        sleep(0.005)
        core.kill()
        the_spawn.join(timeout=5)
        self.assertTrue(core.is_stopped)

        # restart
        the_spawn = spawn(core.run)
        sleep(0.005)
        self.assertFalse(core.is_stopped)
        core.kill()
        the_spawn.join(timeout=5)
        self.assertTrue(core.is_stopped)
