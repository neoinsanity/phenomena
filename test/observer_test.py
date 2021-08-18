from unittest import TestCase

from gevent import joinall, sleep, spawn
import zmq.green as zmq

from phenomena.observer import Observer
from test.utils_of_test import spawn_observer


class ObserverTest(TestCase):
    def setUp(self) -> None:
        self.zmq_ctx = zmq.Context()

    def tearDown(self):
        self.zmq_ctx.destroy()

    def test_init(self):
        o = Observer()
        self.assertIsNotNone(0)

    def test_basic_remote_kill(self):
        # setup a zmq socket to signal a remote kill
        cmd_socket = self.zmq_ctx.socket(zmq.PUB)
        cmd_socket.bind('tcp://*:54749')

        # create the test subject
        the_spawn, observer = spawn_observer(Observer)

        # test for the expected state of the observer in run mode
        self.assertIsNotNone(observer)
        self.assertFalse(observer.is_stopped())

        # send the kill command to the observer instance. because this is a PUB
        # socket, multiple calls maybe required to allow time for connect
        # negotiation between PUB and SUB.
        for _ in range(3):
            cmd_socket.send_string('kill')
            joinall([the_spawn, ], timeout=0.1)
            if the_spawn.successful():  # if spawn is done running
                break;  # exit the message send loop.

        self.assertTrue(the_spawn.successful())
        self.assertIsNone(the_spawn.exception)

        # test that the observer is in the correct stop state
        self.assertTrue(observer.is_stopped())
