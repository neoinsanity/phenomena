from gevent import sleep
import zmq.green as zmq


class Controller(object):
    def __init__(self, event_core, port):
        """

        :param event_core:
        :type event_core: event_core.EventCore
        :param log:
        :type log: logging
        :param port:
        :type port: int
        :return: A valid Controller
        :rtype: Controller
        """
        self.event_core = event_core
        self.log = event_core.log
        self.port = port

        # configure sockets
        self._listener = self.event_core._zmq_ctx.socket(zmq.SUB)
        self._listener.setsockopt(zmq.SUBSCRIBE, '')
        self._listener.bind('tcp://*:%s' % self.port)
        self._sender = self.event_core._zmq_ctx.socket(zmq.PUB)
        self._sender.connect('tcp://localhost:%s' % self.port)

    @property
    def listener(self):
        return self._listener

    def handle_msg(self):
        """
        """
        msg = self._listener.recv()

        if not msg:
            self.log.error('Empty message delivered: %s', msg)
            return

        if msg == '__kill__':
            self.log.info('Received kill message.')
            self.event_core._stopped = True
            return

    def signal_message(self, msg):
        """

        :param msg:
        :type msg: basestring
        :return:
        """
        self._sender.send(msg)

    def close_connections(self):
        self._sender.close()
        self._listener.close()
