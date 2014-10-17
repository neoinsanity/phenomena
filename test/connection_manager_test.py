import unittest

from gevent import sleep, spawn

from phenomena.event_core import EventCore
from phenomena.listener_config import ListenerConfig

import test_utils


class ConnectionManagerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register_listener(self):
        # test subjects
        core = EventCore(command_port=9003)
        listener = core.connection_manager.register_listener()

        # validate listener
        self.assertIsNotNone(listener)

        # validate core state
        # todo: raul - add the rest of the test as the method call us filled.

    def test_register_requester(self):
        # test subjects
        core = EventCore(command_port=9003)
        requester = core.connection_manager.register_requester()

        # validate requester
        self.assertIsNotNone(requester)

        # validate core state
        # todo: raul - add the rest of the test as the method call is filled.

    def test_register_responder(self):
        core = EventCore(command_port=9003)
        responder = core.connection_manager.register_responder()

        # validate responder
        self.assertIsNotNone(responder)

        # validate core state
        # todo: raul - add the rest of the test as the method call is filled.

    def test_register_sink(self):
        # test subjects
        core = EventCore(command_port=9003)
        sink = core.connection_manager.register_sink()

        # validate sink
        self.assertIsNotNone(sink)

        # validate core state
        # todo: raul - add the rest of the test as the method call is filled.
