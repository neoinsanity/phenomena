import logging
import unittest

from gevent import sleep, spawn

from phenomena.event_core import EventCore

class EventCoreTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_event_core(self):

        logging.error('Starting event core test.')
        core = EventCore(log_level='info')

        self.assertIsNotNone(core)

        the_spawn = spawn(core.run)
        sleep(0.1)  # yield to allow the core to configure itself

        core.kill()
        the_spawn.join()
