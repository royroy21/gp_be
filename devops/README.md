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
- Dashboard: `minikube dashboard`

Remember to delete your minikube setup after testing!
- `minikube stop`
- `minikube delete`

### minikube port
Minikube needs to open tunnel for us to access services locally. This isn't needed with production kubernetes.
- `minikube service <deployment-name> --url`

### minikube persistent volumes
Special consideration should be made for persistent volumes when using minikube.
https://minikube.sigs.k8s.io/docs/handbook/persistent_volumes/
- To delete a volume: `kubectl delete pv <name>`

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

# To deploy locally from scratch

### volumes
- `kubectl apply -f devops/volumes/database.yaml`
- `kubectl apply -f devops/volumes/database_claim.yaml`
- `kubectl apply -f devops/volumes/cache.yaml`
- `kubectl apply -f devops/volumes/cache_claim.yaml`

### deployments
- `kubectl apply -f devops/deployments/database.yaml`
- `kubectl apply -f devops/deployments/cache.yaml`
- `kubectl apply -f devops/deployments/gigpig.yaml`
- `kubectl apply -f devops/deployments/worker.yaml`

### services
- `kubectl apply -f devops/services/database.yaml`
- `kubectl apply -f devops/services/cache.yaml`
- `kubectl apply -f devops/services/gigpig.yaml`
