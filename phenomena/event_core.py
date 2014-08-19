""""""
import signal

from cognate.component_core import ComponentCore

from gevent import joinall, sleep, spawn
import zmq.green as zmq

class EventCore(ComponentCore):
    def __init__(self, heartbeat=3, **kwargs):

        self.heartbeat = heartbeat

        # configure the interrupt handlers and shutdown
        self._stopped = True
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)

        ComponentCore.__init__(self, **kwargs)

        # zmq poller used to retrieve messages
        self._poller = None


    def cognate_options(self, arg_parser):
        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=self.heartbeat,
                                help='Set the heartbeat rate in seconds.')
    @property
    def is_stopped(self):
        return self._stopped

    def run(self):
        self._stopped = False

        self.log.info('Execution started with configuration : %s', self)

        # create poller loop
        self._poller = zmq.Poller()
        poller_loop_spawn = spawn(self._poll_loop_executable)

        # initialize the control layer

        # initialize the output sockets

        # initialize the input sockets

        # execute a run loop if one has been assigned

        # set the stop state
        self._stopped = True

        # shutdown input sockets

        # shutdown output sockets

        # shutdown command layer

        # ensure shutdown of poller loop
        joinall([poller_loop_spawn])
        self._poller = None

        self.log.info('Execution terminated.')


    def kill(self):
        self._stopped = True

    def _poll_loop_executable(self):
        while True:
            self._poller.poll(timeout=self.heartbeat * 1000)

            if self._stopped:
                self.log.info('Stop flag triggered ... shutting down.')
                break;

            sleep(0)  # yield to give other spawns a chance to terminate

    def _signal_interrupt_handler(self):
        self.kill()
