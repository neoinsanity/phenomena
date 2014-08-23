import unittest

from gevent import sleep, spawn

from test_utils import StdOutCapture

from phenomena.event_core import EventCore


class EventCoreControllerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_controller_kill_msg(self):
        # test subject
        core = EventCore()
        self.assertIsNotNone(core)

        # start test subject
        the_spawn = spawn(core.run)
        sleep(.005)  # give the spawn a chance to initialize
        self.assertFalse(core.is_stopped)

        # test controller shutdown
        controller = core.controller
        controller.signal_message('__kill__')
        the_spawn.join(timeout=5)

        # ensure that the core is shutdown
        self.assertTrue(core.is_stopped)

    def test_controller_none_msg(self):
        with StdOutCapture() as output:
            # test subject
            core = EventCore(log_level='debug', verbose=True)
            self.assertIsNotNone(core)

            # start test subject
            the_spawn = spawn(core.run)
            sleep(.005)  # give the spawn a chance to initialize
            self.assertFalse(core.is_stopped)

            # test controller shutdown
            controller = core.controller
            controller.signal_message('')
            sleep(0.01)  # allow for processing of the message

            [h.flush() for h in core.log.handlers]
            self.assertFalse(core.is_stopped)

            # ensure that the core is shutdown
            core.kill()
            sleep(0.005)
            the_spawn.join(timeout=5)
            self.assertTrue(core.is_stopped)

        print 'output:', output
