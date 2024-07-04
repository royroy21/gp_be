import logging

from .local import *  # noqa

ENV = "test"

# Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Logging
# Disable all but critical logs when running tests.
logging.disable(logging.CRITICAL)


# Push notifications

PUSH_NOTIFICATIONS_ENABLED = False
CREATE_THUMBNAILS_ENABLED = False
