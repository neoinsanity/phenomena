from ontic.ontic_type import OnticType
from ontic.schema_type import SchemaType


class ListenerConfig(OnticType):
    ONTIC_SCHEMA = SchemaType({
        'id': {
            'type':'int',
        },
        'url': {
            'type': 'str',
            'required': True,
        }
    })
