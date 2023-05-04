from .local import *  # noqa

ENV = "test"

# Elasticsearch configuration
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": "elasticsearch_test:9200",
    },
}

# Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
