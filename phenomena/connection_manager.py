from ontic import ontic_type
from ontic.validation_exception import ValidationException

from input_socket_config import InputSocketConfig


class ConnectionManager(object):
    def __init__(self, event_core):
        self.event_core = event_core
        self.log = event_core.log
        self._input_socket_configs = []
        self._input_index = 0

    @property
    def input_socket_configs(self):
        return self._input_socket_configs

    def register_input_config(self, input_socket_config):
        with self.event_core._config_lock:
            if not isinstance(input_socket_config, InputSocketConfig):
                raise ValueError(
                    '"input_socket_config" must be InputSocketConfig type')

            # validate input
            try:
                ontic_type.validate_object(input_socket_config)
            except ValidationException as ve:
                self.log.exception(ve.message)
                raise ValueError(ve.message)
            #todo: raul - add validation based on socket type

            #todo: raul - add code to determine dynamic addition of socket

            # register the input config
            id = self._input_index
            input_socket_config.id = id
            self._input_socket_configs[id] = input_socket_config
            self._input_index += 1

            return id

