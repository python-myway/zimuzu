import logging

from ext.log import LOGGING


CLIENT_LOGGING = LOGGING
CLIENT_LOGGING.update({
    'loggers': {
        'client': {
            'level': 'INFO',
            'handlers': ['internal', 'errorStream']
        },
    }
})

log = logging.getLogger('client')
