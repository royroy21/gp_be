# Django backend for GP

## Chat logic [here](project/chat/README.md).

## Redis server: notes on docker configuration [here](redis/README.md).

## Local Data
On first local install if you need test data run the following commands:
- `make manage ARGS="import_country_codes"`
- `make manage ARGS="import_genres"`
- `make manage ARGS="create_fake_gigs"`

## Kubernetes
This project can be started and tested locally using minikube.
For instructions on how to do this view the readme [here](devops/README.md).
