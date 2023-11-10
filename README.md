# Django backend for GP

## Chat logic [here](project/chat/README.md).

## Redis server: notes on docker configuration [here](redis/README.md)

## Docker compose with elasticsearch
Elastic search will error with a `max-virtual-memory` error when running docker compose. 
To fix this do the following:

Edit /etc/sysctl.conf and set the following `vm.max_map_count=262144`

## Local Data
On first local install if you need test data run the following commands:
- `make manage ARGS="import_country_codes"`
- `make manage ARGS="import_genres"`
- `make manage ARGS="create_fake_gigs"`
