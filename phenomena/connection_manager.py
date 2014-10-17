from ontic import ontic_type
from ontic.validation_exception import ValidationException

from phenomena.connection_types import Listener, Requester, Responder, Sink
from listener_config import ListenerConfig


class ConnectionManager(object):
    def __init__(self, event_core):
        """

        :param event_core:
        :type event_core: phenomena.event_core.EventCore
        """
        self.event_core = event_core
        self.log = event_core.log
        self._input_socket_configs = {}
        self._input_index = 0

    @property
    def input_socket_configs(self):
        return self._input_socket_configs

    def register_input_config(self, input_socket_config):
        with self.event_core._config_lock:
            if not isinstance(input_socket_config, ListenerConfig):
                raise ValueError(
                    '"input_socket_config" must be ListenerConfig type')

            # Validate input
            try:
                ontic_type.validate_object(input_socket_config)
            except ValidationException as ve:
                self.log.error(ve.message)
                raise ValueError(ve.message)

            # todo: raul - add validation based on socket type

            # todo: raul - add code to determine dynamic addition of socket

            # register the input config
            id = self._input_index
            input_socket_config.id = id
            self._input_socket_configs[id] = input_socket_config
            self._input_index += 1

            return id

    def register_listener(self):
        listener = Listener()
        #todo: raul - add the actual code
        return listener

    def register_requester(self):
        requester = Requester()
        #todo: raul - add the actual code
        return requester

    def register_responder(self):
        responder = Responder()
        #todo: raul - add the actual code
        return responder

    def register_sink(self):
        sink = Sink()
        #todo: raul - add the actual code
        return sink
