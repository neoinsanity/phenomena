import json
import unittest

from gevent import sleep, spawn

from phenomena.command_message import CommandMessage
from phenomena.event_core import EventCore

import test_utils


class ControllerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_controller_kill_msg(self):
        # test subject
        core = EventCore(command_port=9002)
        self.assertIsNotNone(core)

        # start test subject
        the_spawn = spawn(core.run)
        sleep(.005)  # give the spawn a chance to initialize
        self.assertFalse(core.is_stopped)

        # test controller shutdown
        controller = core.controller
        kill_cmd = CommandMessage(cmd = CommandMessage.CMD_KILL)
        controller.signal_message(kill_cmd)
        the_spawn.join(timeout=5)

        # ensure that the core is shutdown
        self.assertTrue(core.is_stopped)

    def test_controller_none_msg(self):
        log = test_utils.create_capture_log()

        # test subject
        core = EventCore(log=log)
        self.assertIsNotNone(core)

        # start test subject
        the_spawn = spawn(core.run)
        sleep(.005)  # give the spawn a chance to initialize
        self.assertFalse(core.is_stopped)

        # test controller shutdown
        controller = core.controller
        controller.signal_message({})
        sleep(0.01)  # allow for processing of the message

        self.assertFalse(core.is_stopped)

        # ensure that the core is shutdown
        core.kill()
        sleep(0.005)
        the_spawn.join(timeout=5)
        self.assertTrue(core.is_stopped)

        self.assertListEqual(['Empty command message delivered.'],
                             log.capture_handle.read_messages())
