from argparse import ArgumentParser
import signal

from cognate import ComponentCore
from gevent import joinall, spawn
import zmq.green as zmq

#: Mapping for zmq_socket_types
ZMQ_INPUT_SOCKET_TYPE = {
    'pull': zmq.PULL,
    'rep': zmq.REP,
    'sub': zmq.SUB,
    'router': zmq.ROUTER,
}

ZMQ_OUTPUT_SOCKET_TYPE = {
    'pub': zmq.PUB,
    'push': zmq.PUSH,
    'req': zmq.REQ,
    'dealer': zmq.REQ,
}

DEFAULT_INPUT_OPTIONS = {
    'url': 'tcp://localhost:60053',
    'sock_type': 'pull',
    'sock_filter': '',
    'sock_bind': False,
    'linger': 0,
    'monitor_stream': False,
    'no_block_send': False,
}

DEFAULT_OUTPUT_OPTIONS = {
    'url': 'tcp://localhost:60053',
    'sock_type': 'push',
    'sock_bind': False,
    'linger': 0,
    'monitor_stream': False,
    'no_block_send': False,
}


class _ObserverRunStateLayer(ComponentCore):
    def __init__(self, **kwargs: dict):
        # configure the interrupt handling
        self._stop = True
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)

        super().__init__(**kwargs)

    @property
    def should_stop(self):
        return self._stop

    def kill(self):
        """
        This method will shut down the running loop if run() method has been
        invoked.
        """
        self._stop = True

    def _signal_interrupt_handler(self, signum, frame):
        """
        This method is registered with the signal library to ensure handling
        of system interrupts. Initialization of this method is performed
        during __init__ invocation.
        """
        self.kill()


class _ObserverConnectionLayer(_ObserverRunStateLayer):
    def __init__(self, **kwargs):

        self._blades = dict()
        self._cargos = dict()
        self._control_sock = None
        self._command_handler = None

        self._zmq_ctx = zmq.Context()
        self._poll = zmq.Poller()

        super().__init__(**kwargs)

    def register_command_handler(self, command_handler=None):
        """

        :param command_handler:
        :type command_handler: MethodType or FunctionType
        """
        assert command_handler
        self._command_handler = command_handler

    def get_input_socket(self, socket_options):
        """

        :param socket_options:
        :return:
        :rtype: zmq.Socket, InputSocketConfig
        """

        socket_config = InputSocketConfig(socket_options)
        InputSocketConfig.validate(socket_config)

        input_sock = self._zmq_ctx.socket(socket_config.zmq_sock_type)
        input_sock.linger = socket_config.linger

        port = None
        if socket_config.sock_bind:
            if socket_config.url.endswith('*'):
                port = input_sock.bind_to_random_port(socket_config.url,
                                                      min_port=200000,
                                                      max_port=250000)
            else:
                input_sock.bind(socket_config.url)
        else:
            input_sock.connect(socket_config.url)

        # actual creation and recording of Cargo
        if not port:
            port = re.match('.*?([0-9]+)$', socket_config.url).group(1)

        socket_config.port = port

        return input_sock, socket_config

    def get_output_sock(self, socket_options):
        """

        :param socket_options:
        :type socket_options: dict
        :return:
        :rtype: zmq.Socket, OutputSocketConfig
        """
        # create and store the socket
        socket_config = OutputSocketConfig(socket_options)
        OutputSocketConfig.validate(socket_config)
        output_sock = self._zmq_ctx.socket(socket_config.zmq_sock_type)
        output_sock.linger = socket_config.linger

        port = None
        if socket_config.sock_bind:
            if socket_config.url.endswith('*'):
                port = output_sock.bind_to_random_port(socket_config.url,
                                                       min_port=200501,
                                                       max_port=300000)
            else:
                output_sock.bind(socket_config.url)
        else:
            output_sock.connect(socket_config.url)

        # ensure the socket can be used for sending
        self._poll.register(output_sock, zmq.POLLOUT)

        # actual creation and recording of Cargo
        if not port:
            port = re.match('.*?([0-9]+)$', socket_config.url).group(1)

        socket_config.port = port

        return output_sock, socket_config

    def send_crate(self, delivery_key, crate):
        assert delivery_key
        assert crate

        # todo: raul -  create socket/retrieve socket for now
        sock, socket_config = self._cargos.get(delivery_key)

        # todo: raul - then send crate
        msg = crate.dump

        for cnt in range(3):
            self.log.debug('poll check on socket(%s): %s', cnt, sock)
            socks = dict(self._poll.poll())
            if socks.get(sock) == zmq.POLLOUT:
                self._send(msg, sock, socket_config)
                break

    def _send(self, msg, sock, sock_config):
        assert msg

        if not sock_config.no_block_send:
            self.log.debug('Block sending: %s', msg)
            sock.send_json([msg])
        else:
            self.log.debug('No Block sending: %s', msg)
            try:
                sock.send_json([msg], zmq.NOBLOCK)
            except zmq.ZMQError as ze:
                self.log.exception('ZMQ error detection: %s', ze)
            except Exception as e:
                self.log.exception('Unexpected exception: %s', e)

    def run_poll_loop(self, socks_handler_map, heartbeat):
        """

        :param socks_handler_map:
        :type socks_handler_map: dict
        :param heartbeat:
        :type heartbeat: int
        """
        print(('run_poll_loop: %s, %s' % (socks_handler_map, heartbeat)))
        while True:
            try:
                socks = dict(self._poll.poll(timeout=heartbeat * 1000000))
                for input_sock in list(socks_handler_map.keys()):
                    if socks.get(input_sock) == zmq.POLLIN:
                        msg = socks_handler_map[input_sock].recv_handler(
                            input_sock)

                if (self._control_sock and socks.get(
                        self._control_sock) == zmq.POLLIN):
                    msg = self._control_sock.recv()
                    self.log.info('Command msg: %s', msg)
                    if self._command_handler is not None:
                        self._command_handler(msg)
                        if self.should_stop:
                            break

                if self.should_stop:
                    self.log.info('Stop flag triggered ... shutting down.')
                    break

            except zmq.ZMQError as ze:
                if ze.errno == 4:  # Known exception due to keyboard ctrl+c
                    self.log.info('System interrupt call detected.')
                else:  # exit hard on unhandled exceptions
                    self.log.error(
                        'Unhandled exception in run execution:%d - %s' % (
                            ze.errno, ze.strerror))
                    exit(-1)


class Observer(_ObserverConnectionLayer):
    def __init__(self, **kwargs):

        self._bricks = list()
        self._cornerstone = None

        # configure the interrupt handling
        self._stop = True
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)

        #: a heartbeat interval that will be relaid to control channel
        self.heartbeat = 1

        super().__init__(**kwargs)

        # set the default handler, if name has been assigned.
        self.register_command_handler(self._default_command_handler)

    def cognate_options(self, arg_parser: ArgumentParser):
        assert arg_parser

        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=self.heartbeat,
                                help='Set the heartbeat rate in seconds.')

    def cognate_configure(self, args):
        assert args

        self.log.debug('... shaft configuration complete ...')

    def declare_blade(self, handler=None, socket_options=DEFAULT_INPUT_OPTIONS):
        """

        :param handler:
        :type handler: MethodType or FunctionType
        :param socket_options:
        :type socket_options: dict
        """
        if handler == None:
            raise ValueError('Must pass handler method to be called to accept '
                             'received Cargo object.')

        self.log.info('... Configuring socket options: %s', socket_options)

        blade_sock, socket_config = self.get_input_socket(socket_options)

        blade = Blade(handler=handler, socket_config=socket_config)
        self._blades[blade] = (blade_sock, socket_config)

        return blade

    def declare_brick(self, target, *args, **kwargs):

        self.log.info('... Configuring brick: %s, %s, %s', target, args, kwargs)

        brick = Brick(func=target, *args, **kwargs)

        self._bricks.append(brick)

    def declare_cargo(self, socket_options=DEFAULT_OUTPUT_OPTIONS):

        self.log.info('... Configuring cargo socket: %s', socket_options)

        # abstract handle to allow cargo instance to deliver a message
        delivery_key = randint(-maxsize - 1, maxsize)
        delivery_handler = DeliveryHandler(delivery_key=delivery_key,
                                           send_func=self.send_crate)

        cargo_sock, socket_config = self.get_output_sock(socket_options)

        cargo = Cargo(delivery_handle=delivery_handler.send_crate,
                      socket_config=socket_config)
        self._cargos[delivery_key] = (cargo_sock, socket_config)
        return cargo

    def declare_cornerstone(self, target, *args, **kwargs):
        self._cornerstone = Cornerstone(target, *args, **kwargs)

    def is_stopped(self):
        return self._stop

    def run(self):
        self._stop = False

        self.log.info('Beginning run() with configuration: %s', self)
        # initialize the input sockets
        socks_handler_map = dict()
        for blade in list(self._blades.keys()):
            blade_sock, socket_config = self._blades[blade]
            self.log.debug('Initialize socket: %s', socket_config)
            self._poll.register(blade_sock, zmq.POLLIN)
            socks_handler_map[blade_sock] = blade

        # todo: raul - move this section to command configuration layer
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # of course this is when a command configuration layer get's added
        controller = self._zmq_ctx.socket(zmq.SUB)
        controller.connect('tcp://localhost:54749')
        controller.setsockopt_string(zmq.SUBSCRIBE, '')
        self._control_sock = controller
        self._poll.register(self._control_sock, zmq.POLLIN)
        self.log.info('Configured cmd socket')
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self.log.info('Entering run loop')

        # start all of the bricks
        for brick in self._bricks:
            brick.start()

        poller_loop_spawn = spawn(self._run_poll_loop, socks_handler_map)

        if self._cornerstone is not None:
            cornerstone_spawn = spawn(self._cornerstone.run)
            joinall([cornerstone_spawn])
            self._stop = True
        else:
            joinall([poller_loop_spawn])

        # stop the running bricks
        for brick in self._bricks:
            brick.stop()

        # close the sockets held by the poller
        self._control_sock.close()
        for sock in list(socks_handler_map.keys()):
            sock.close()

        for sock, socket_config in list(self._cargos.values()):
            sock.close()

        self.log.info('Run terminated for %s', self.__class__.__name__)

    def kill(self):
        """
        This method will shut down the running loop if run() method has been
        invoked.
        """
        self.log.debug('kill has been invoked.')
        self._stop = True

    def _run_poll_loop(self, socks_handler_map):

        while True:
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat * 1000))

                for input_sock in list(socks_handler_map.keys()):
                    if socks.get(input_sock) == zmq.POLLIN:
                        msg = socks_handler_map[input_sock].recv_handler(
                            input_sock)

                if (self._control_sock and socks.get(
                        self._control_sock) == zmq.POLLIN):
                    msg = self._control_sock.recv()
                    self.log.info('Command msg: %s', msg)
                    if self._command_handler is not None:
                        self._command_handler(msg)
                        if self._stop:
                            break

                if self._stop:
                    self.log.info('Stop flag triggered ... shutting down.')
                    break

                sleep(0)  # yield to give other spawns a chance to execute

            except zmq.ZMQError as ze:
                if ze.errno == 4:  # Known exception due to keyboard ctrl+c
                    self.log.info('System interrupt call detected.')
                else:  # exit hard on unhandled exceptions
                    self.log.error(
                        'Unhandled exception in run execution:%d - %s' % (
                            ze.errno, ze.strerror))
                    exit(-1)

    def _signal_interrupt_handler(self, signum, frame):
        """
        This method is registered with the signal library to ensure handling
        of system interrupts. Initialization of this method is performed
        during __init__ invocation.
        """
        self.kill()

    def _default_command_handler(self, msg):
        """
        This method is the default command channel message handler. It simply
        invokes a kill flag for any message received.
        """
        # todo: add real command handler.
        ## Most likely one based on passing a struct like {'command':'foo', 'params': {..}}
        self.log.debug('Got the kill command.')
        self.kill()
