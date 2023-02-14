from .local import *  # noqa

ENV = "test"

# Elasticsearch configuration
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": "elasticsearch_test:9200",
    },
}
