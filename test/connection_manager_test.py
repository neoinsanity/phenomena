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

    def test_simple_input_connection(self):
        # test subject
        core = EventCore(command_port=9003)
        self.assertIsNotNone(core)

        # configure the input socket
        socket_config = ListenerConfig()
        core.connection_manager.register_input_config(socket_config)
