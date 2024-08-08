# Docker.
This project uses containers that are stored in private hub.

### To build a local docker image before pushing to docker hub
- `docker build -t <container>:tag .` 
- Example: `docker build -t royhanley8/gp_be:latest .` NOTE: this tags the image also.

### To tag an image
If you want to tag the image with another tag use:
- `docker tag <container> <username>/<name>:<tag>` 
- Example `docker tag royhanley8/gp_be:latest royhanley8/gp_be:latest`

### To push an image
- `docker push <username>/<name>:<tag>` 
- Example `docker push royhanley8/gp_be:latest`

### Image not updating
If the image doesn't want to update try pruning volumes and trying again.
- `docker system prune -a --volumes`

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
- `kubectl apply -f devops/minikube/deployments/<file>.yaml`
- `kubectl apply -f devops/minikube/services/<file>.yaml`

### ssh into pod
- `kubectl exec -it <pod-name> -- /bin/bash`

# To deploy locally from scratch

### minikube
We need to create volumes on the host minikube machine for 
Django's static and media directories.
- `minikube ssh`
- `mkdir static; chmod -R 777 static`
- `mkdir media; chmod -R 777 media`
- `mkdir postgres; chmod -R 777 postgres`
- `mkdir redis; chmod -R 777 redis`

### config maps
- `kubectl apply -f devops/minikube/configmaps/nginx.yaml`

### volumes
- `kubectl apply -f devops/minikube/volumes/media.yaml`
- `kubectl apply -f devops/minikube/volumes/media_claim.yaml`
- `kubectl apply -f devops/minikube/volumes/static.yaml`
- `kubectl apply -f devops/minikube/volumes/static_claim.yaml` 
- `kubectl apply -f devops/minikube/volumes/postgres.yaml`
- `kubectl apply -f devops/minikube/volumes/postgres_claim.yaml`
- `kubectl apply -f devops/minikube/volumes/redis.yaml`
- `kubectl apply -f devops/minikube/volumes/redis_claim.yaml`
 
### deployments
- `kubectl apply -f devops/minikube/deployments/postgres.yaml`
- `kubectl apply -f devops/minikube/deployments/redis.yaml`
- `kubectl apply -f devops/minikube/deployments/django.yaml`
- `kubectl apply -f devops/minikube/deployments/worker.yaml`
- `kubectl apply -f devops/minikube/deployments/nginx.yaml`

### services
- `kubectl apply -f devops/minikube/services/postgres.yaml`
- `kubectl apply -f devops/minikube/services/redis.yaml`
- `kubectl apply -f devops/minikube/services/django.yaml`
- `kubectl apply -f devops/minikube/services/nginx.yaml`
