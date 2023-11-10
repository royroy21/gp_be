# Django backend for GP

## Chat logic [here](project/chat/README.md).

## Redis server: notes on docker configuration [here](redis/README.md)

## Docker compose with elasticsearch
Elastic search will error with a `max-virtual-memory` error when running docker compose. 
To fix this do the following:

Edit /etc/sysctl.conf and set the following `vm.max_map_count=262144`