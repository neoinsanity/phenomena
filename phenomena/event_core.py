""""""
import signal

from cognate.component_core import ComponentCore
from decorator import decorator
from gevent import sleep, spawn
from gevent.lock import RLock
import zmq.green as zmq

from command_message import CommandMessage
from controller import Controller
from connection_manager import ConnectionManager


@decorator
def config_lock(func, self, *args, **kwargs):
    with self._config_lock:
        return func(self, *args, **kwargs)


class EventCore(ComponentCore):
    def __init__(self, command_port=60053, heartbeat=3, **kwargs):

        # initialize configurable attributes
        self.heartbeat = heartbeat
        self.command_port = command_port

        # execute the event core configuration
        ComponentCore.__init__(self, **kwargs)

        # configure the interrupt handlers and run state
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)
        self._stopped = True

        # zmq context used to create sockets
        self._zmq_ctx = None

        # zmq poller used to retrieve messages
        self._poller = None

        # semaphore for controlling configuration
        self._config_lock = RLock()

        # the service controller
        self._controller = None

        # input configs are of type input_socket_config.ListenerConfig
        self._connection_manager = ConnectionManager(self)
        self._input_sockets = None

    def cognate_options(self, arg_parser):
        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=self.heartbeat,
                                help='Set the heartbeat rate in seconds.')

    @property
    def controller(self):
        return self._controller

    @property
    def connection_manager(self):
        return self._connection_manager

    @property
    def is_stopped(self):
        return self._stopped

    def run(self):
        self._stopped = False

        self.log.info('Execution started with configuration : %s', self)

        # create the zmq context
        self._zmq_ctx = zmq.Context()

        # create poller loop
        self._poller = zmq.Poller()

        with self._config_lock:
            # initialize the control layer
            self._controller = Controller(event_core=self,
                                          port=self.command_port)
            self._poller.register(self._controller.listener, zmq.POLLIN)

            # initialize the output sockets

            # initialize the input sockets
            self._input_sockets = []
            for sock_config in self._connection_manager.input_socket_configs:
                self.log.info('Configuring socket: %s', sock_config)
                # todo: raul - add actual socket creation logic

            # spawn the poller loop
            poller_loop_spawn = spawn(self._poll_loop_executable)
            sleep(0)

        # execute a run loop if one has been assigned
        # else wait for the poll loop to exit
        # ensure shutdown of poller loop
        poller_loop_spawn.join()
        self._clear_poller()

        with self._config_lock:
            # shutdown input sockets
            for sock in self._input_sockets:
                sock.close()

            self._input_sockets = None

            # shutdown output sockets

            # shutdown command layer
            self._controller.close_connections()
            self._controller = None

        # destroy poller
        self._poller = None

        # destroy zmq context
        self._zmq_ctx = None

        self.log.info('Execution terminated.')

    @config_lock
    def kill(self):
        #with self._config_lock:
        self.log.info('kill invoked.')
        kill_cmd = CommandMessage(cmd=CommandMessage.CMD_KILL)
        self._controller.signal_message(kill_cmd)

    def _clear_poller(self):
        self.log.info('Clearing poller.')

        count = 3
        while count > 0:
            count -= 1

            socks = dict(self._poller.poll(timeout=0.25))
            msg_found = False
            for sock in self._input_sockets:
                if socks.get(sock) == zmq.POLLIN:
                    msg_found = True
                    # todo: raul - add processing of message
                    spawn(sock.recv_handler, sock)

            if msg_found:
                count = 3

    def _poll_loop_executable(self):
        self.log.info('Starting run loop.')
        self._stopped = False
        while not self._stopped:
            socks = dict(self._poller.poll(timeout=self.heartbeat * 1000))

            if socks.get(self._controller.listener) == zmq.POLLIN:
                self._controller.handle_msg()

            for sock in self._input_sockets:
                if socks.get(sock) == zmq.POLLIN:
                    # todo: raul - add processing of msg
                    spawn(sock.recv_handler, sock)

            self.log.debug('Thump!, Thump!')

        self.log.info('Run loop shutdown.')
        sleep(0)  # yield to give other spawns a chance to terminate

    def _signal_interrupt_handler(self):
        self.kill()
