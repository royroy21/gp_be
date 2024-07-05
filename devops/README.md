# Docker.
This project uses containers that are stored in private hub.

### To build a local docker image before pushing to docker hub
- `docker build -t <container>:tag .` 
- Example: `docker build -t gigpig:latest .` 

### To tag an image
- `docker tag <container> <username>/<name>:<tag>` 
- Example `docker tag gigpig royhanley8/gp_be:latest`

### To push an image
- `docker push <username>/<name>:<tag>` 
- Example `docker push royhanley8/gp_be:latest`

# Kubernetes.
https://kubernetes.io/docs/tutorials/

### To give kubectl access to docker hub follow instructions here
https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

# Minikube
To test kubernetes configuration locally minikube is used.
- Start: `minikube start`
- Access dashboard: `minikube dashboard`

### minikube port
Minikube needs to open tunnel for us to access services locally. This isn't needed with production kubernetes.
- `minikube service <deployment-name> --url`

### kubectl
Various kubernetes commands:
- `kubectl get deployments`
- `kubectl get pods`
- `kubectl get events`
- `kubectl config view`
- `kubectl get services`
- `kubectl logs <pod-name> -c <container-name>`

### Applying devops folder deployments and services yaml files.
- `kubectl apply -f devops/deployments/<file>.yaml`
- `kubectl apply -f devops/services/<file>.yaml`

### ssh into pod
- `kubectl exec -it <pod-name> -- /bin/bash`
