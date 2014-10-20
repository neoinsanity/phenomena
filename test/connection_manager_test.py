import unittest

from phenomena.event_core import EventCore


class ConnectionManagerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register_default_listener(self):
        # test subjects
        core = EventCore(command_port=63353)
        listener = core.connection_manager.register_listener()

        # validate listener
        self.assertIsNotNone(listener)
        self.assertEqual('localhost', listener.address)
        self.assertIs(long, type(listener.id))
        self.assertEqual(60053, listener.port)
        self.assertEqual('tcp', listener.protocol)
        self.assertEqual('pull', listener.type)

        # validate core state
        # todo: raul - add the rest of the test as the method call us filled.

    def test_register_default_requester(self):
        # test subjects
        core = EventCore(command_port=63353)
        requester = core.connection_manager.register_requester()

        # validate requester
        self.assertIsNotNone(requester)
        self.assertEqual('localhost', requester.address)
        self.assertIs(long, type(requester.id))
        self.assertEqual(60053, requester.port)
        self.assertEqual('tcp', requester.protocol)
        self.assertEqual('request', requester.type)

        # validate core state
        # todo: raul - add the rest of the test as the method call is filled.

    def test_register_default_responder(self):
        core = EventCore(command_port=63353)
        responder = core.connection_manager.register_responder()

        # validate responder
        self.assertIsNotNone(responder)
        self.assertEqual('*', responder.address)
        self.assertIs(long, type(responder.id))
        self.assertEqual(60053, responder.port)
        self.assertEqual('tcp', responder.protocol)
        self.assertEqual('reply', responder.type)

        # validate core state
        # todo: raul - add the rest of the test as the method call is filled.

    def test_register_default_sink(self):
        # test subjects
        core = EventCore(command_port=63353)
        sink = core.connection_manager.register_sink()

        # validate sink
        self.assertIsNotNone(sink)
        self.assertEqual('*', sink.address)
        self.assertIs(long, type(sink.id))
        self.assertEqual(60053, sink.port)
        self.assertEqual('tcp', sink.protocol)
        self.assertEqual('push', sink.type)

        # validate core state
        # todo: raul - add the rest of the test as the method call is filled.
