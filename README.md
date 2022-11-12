# lk8s

All you need for a local Kubernetes setup in one place

## Table of Contents

1. [Kubernetes basics and concepts](#kubernetes-basics-and-concepts)
2. [Prerequisites](#prerequisites)
3. [Repository structure](#repository-structure)
4. [Getting started](#getting-started)
5. [Local containers](#local-containers)
6. [Port forwarding](#port-forwarding)
7. [Access pod B from another pod A](#access-pod-b-from-another-pod-a)
8. [Access host resources from a pod](#access-host-resources-from-a-pod)
9. [Logs](#logs)

## Kubernetes basics and concepts

A Kubernetes cluster consists of a set of worker machines, called
[Nodes](https://kubernetes.io/docs/concepts/architecture/nodes/), that run
containerized applications. Containers are placed into
[Pods](https://kubernetes.io/docs/concepts/workloads/pods/) and usually managed
by
[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
A deployment declares the number of replicas of an app that should be running at
a time, it then automatically spins up the requested pods and monitors them. If
a pod crashes, the deployment will automatically re-create it. A
[Service](https://kubernetes.io/docs/concepts/services-networking/service/)
resource can be used as an abstraction layer to manage network traffic to a set
of pods. Furthermore, an
[Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
exposes HTTP and HTTPS routes from outside the cluster to services within the
cluster. Traffic routing is controlled by rules defined on the Ingress resource,
for instance traffic to the URL path `/foo` can be routed to a `foo` service
while traffic to `/bar` can be routed to a `bar` service.

[![](https://mermaid.ink/img/pako:eNqNkl1vwiAUhv8KwRtNWueqWwwuXrkLk2Ux83L1gpZTJVJogO4j6n8fFRptsq8bODk873vgHA44VwwwwVtNqx16epmlEqFccJC2_-r3zSAeoqXcajAmLqmkW2DoIdNzJBRlKKOCyhw0GsZz7qnXFAce9Z-d_3JFmm2ltB2keHOuEdA4nh9vCqWOBvQbz-HWadc-RH2XJ9PRt5KM6laSXEtc_lpi6sy_LBe1saCvbPx5qOo8K8Wa4ivFzoURraqLTQdL_sASj41bzN3pF2zyEwaS-WFQYxZQoEpQLlHBhSA9xlhkrFZ7IL2iKEIcv3Nmd2RSfUS5EkqT3mg0mnVM9lMTLMbJfQ53_3JxZ12X0M3gdJGSXpZlXZvkYuMrXpzaSURte9sgiZphNMs5GjfLpLn6ldb_Td-UTtrfLOwzHOESdEk5c5_80HAptjsoIcXEhQwKWgub4lSeHFpXjFp4ZNwqjUlBhYEI09qq9afMMbG6hhZacOp-Vhmo0xedox4L)](https://mermaid.live/edit#pako:eNqNkl1vwiAUhv8KwRtNWueqWwwuXrkLk2Ux83L1gpZTJVJogO4j6n8fFRptsq8bODk873vgHA44VwwwwVtNqx16epmlEqFccJC2_-r3zSAeoqXcajAmLqmkW2DoIdNzJBRlKKOCyhw0GsZz7qnXFAce9Z-d_3JFmm2ltB2keHOuEdA4nh9vCqWOBvQbz-HWadc-RH2XJ9PRt5KM6laSXEtc_lpi6sy_LBe1saCvbPx5qOo8K8Wa4ivFzoURraqLTQdL_sASj41bzN3pF2zyEwaS-WFQYxZQoEpQLlHBhSA9xlhkrFZ7IL2iKEIcv3Nmd2RSfUS5EkqT3mg0mnVM9lMTLMbJfQ53_3JxZ12X0M3gdJGSXpZlXZvkYuMrXpzaSURte9sgiZphNMs5GjfLpLn6ldb_Td-UTtrfLOwzHOESdEk5c5_80HAptjsoIcXEhQwKWgub4lSeHFpXjFp4ZNwqjUlBhYEI09qq9afMMbG6hhZacOp-Vhmo0xedox4L)

## Prerequisites

- [docker](https://docs.docker.com/get-docker/)
- [k3d](https://k3d.io/) to setup a local Kubernetes cluster
- [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) to communicate with
  the cluster
- port `8080` and `8443` must not be in use

## Repository structure

```
├── apps
│   ├── hello
│   ├── whoami 
│   └── wordpress
└── infrastructure
    ├── ingress-nginx
    └── kubernetes-dashboard
```

- `apps` contains applications
  - [hello](./my-containers/hello/) container mainteined locally in
    `/my-containers` directory
  - [whoami](https://hub.docker.com/r/traefik/whoami) container maintained by
  3rd parties and pulled from public registries
  - [wordpress](https://hub.docker.com/r/bitnami/wordpress/) container with
    [persistent
    volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- `infrastructure` contains common tools
  - [ingress-nginx](https://kubernetes.github.io/ingress-nginx/) controller
  - [Kubernetes
  Dasboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)

The separation between apps and infrastructure makes it possible to deploy
resources in a certain order.

## Getting started

Start a local Kubernetes cluster 
```shell
k3d cluster create --config k3d-config.yaml
```

Apply infrastructure manifests
```shell
kubectl apply --kustomize infrastructure
```

### Setup secrets
HashiCorp [Vault](https://developer.hashicorp.com/vault) is a secret management
tool that will manage all secrets. Before it can be used, the vault must be
initilized and unsealed, see [vault
docs](https://developer.hashicorp.com/vault/docs/concepts/seal#seal-unseal) for
more details. The Vault Web UI can be reached at
[`http://vault.127.0.0.1.nip.io:8080/`](http://vault.127.0.0.1.nip.io:8080/)

Initialize vault
```shell
kubectl exec deployment/vault --namespace vault -- \
  vault operator init \
    -key-shares=1 \
    -key-threshold=1 \
    -format=json > volumes/storage/vault/cluster-keys.json
```

> Note: Do not run an unsealed Vault in production with a single key share and a single key threshold

Capture unseal key in a variable
```shell
VAULT_UNSEAL_KEY=$(cat volumes/storage/vault/cluster-keys.json | jq -r ".unseal_keys_b64[]")
```

Unseal vault
```shell
kubectl exec deployment/vault --namespace vault -- vault operator unseal $VAULT_UNSEAL_KEY
```

Capture root token in a variable
```shell
VAULT_TOKEN=$(cat volumes/storage/vault/cluster-keys.json | jq -r ".root_token")
```

Enable kv secrets engine at path `secret`
```shell
kubectl exec deployment/vault --namespace vault -- \
  env VAULT_TOKEN=$VAULT_TOKEN \
  vault secrets enable -path=secret kv-v2
```

Populate example secrets for each app with a `.secret.example.json` file, modify
as needed using Web UI
```shell
for SECRET in $(find apps -type f -name ".secret.example.json")
do
  SECRET_NAME=$(basename $(dirname $SECRET))
  curl \
    --header "X-Vault-Token: $VAULT_TOKEN" \
    --header "Content-Type: application/merge-patch+json" \
    --request POST \
    --data @$SECRET \
    http://vault.127.0.0.1.nip.io:8080/v1/secret/data/$SECRET_NAME
done
```

Inject secrets into Kubernetes Pods with [external-secrets](https://external-secrets.io/)

Enable the Kubernetes authentication method
```shell
kubectl exec deployment/vault --namespace vault -- \
  env VAULT_TOKEN=$VAULT_TOKEN \
  vault auth enable kubernetes
```

Configure the Kubernetes authentication method, `KUBERNETES_PORT_443_TCP_ADDR`
is defined and references the internal Kubernetes API
```shell
kubectl exec deployment/vault --namespace vault -- \
  env VAULT_TOKEN=$VAULT_TOKEN \
  vault write auth/kubernetes/config kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
```

Create a readonly policy
```shell
curl \
  --header "X-Vault-Token: $VAULT_TOKEN" \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{ "policy": "path \"secret/*\" { capabilities = [\"read\"] }" }' \
  http://vault.127.0.0.1.nip.io:8080/v1/sys/policy/readonly
```

Create an authentication role `k8s-role` that connects the service account `*`
and attach the policy `readonly`
```shell
curl \
  --header "X-Vault-Token: $VAULT_TOKEN" \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{ "bound_service_account_names": "*", "bound_service_account_namespaces": "*", "policies": ["readonly"] }' \
  http://vault.127.0.0.1.nip.io:8080/v1/auth/kubernetes/role/k8s-role
```


Apply apps manifests
```shell
kubectl apply --kustomize apps
```





<!-- ########################################################################################################### -->


## Getting started

Start a local Kubernetes cluster 
```shell
k3d cluster create --config k3d-config.yaml
```

Copy `.env` file for each app and configure env variables as needed
```shell
find apps -type f -name ".env.example" -exec sh -c 'cp --no-clobber ${1} ${1%/*}/.env' sh_cp {} \;
```

Apply manifests, to delete resources replace `apply` with `delete`
```shell
kubectl apply --kustomize infrastructure
```

```shell
kubectl apply --kustomize apps
```

Wait for apps to be ready before proceeding
```shell
kubectl wait --for=condition=Available=true --timeout=1m --namespace apps deployment/whoami
```

Hit `whoami` pod over HTTP
```shell
curl "http://whoami.127.0.0.1.nip.io:8080"
```

Hit `whoami` pod over HTTPS
```shell
curl --insecure "https://whoami.127.0.0.1.nip.io:8443"
```

Access `Kubernetes Dashboard` at
[`http://kubernetes.127.0.0.1.nip.io:8080/dashboard/`](http://kubernetes.127.0.0.1.nip.io:8080/dashboard/)

Access `Wordpress` at [`http://wordpress.127.0.0.1.nip.io:8080/`](http://wordpress.127.0.0.1.nip.io:8080/)

### Local containers

Images are usually built and pushed into a registry and then pulled (downloaded)
by a Kubernetes cluster. But when developing locally one can instead use a local
registry. K3d has already created one, view it with `docker ps --filter
name=registry`.

Build images located in the `/my-containers` directory
```shell
for DIR in my-containers/**; do docker build --tag ${DIR##*/} --tag localhost:5000/${DIR##*/} $DIR; done
```

> Note: Each directory inside `/my-containers` must contain a Dockerfile, the directory
> name is used as the image name and images are tagged with the `latest` tag.

Push images to the local registry
```shell
for DIR in my-containers/**; do docker push localhost:5000/${DIR##*/}; done
```

> Note: To list images in the local registry use `curl
> "http://localhost:5000/v2/_catalog"`

Deploy `hello` app
```shell
kubectl apply --kustomize apps/hello
```

> Note: If a container inside `/my-containers` is modified make sure to first
> re-build the image, then re-push it to the local registry, then destroy the
> related deployment resource and lastly re-apply it. Otherwise changes won't be
> detected because deployments are (for simplicity) configured to use the
> `latest` tag instead of unique tags.

Hit `hello` pod over HTTP
```shell
curl "http://hello.127.0.0.1.nip.io:8080/v1/echo"
```

### Port forwarding

Some apps are not supposed to be exposed outside the cluster such as a database
or an internal api. In these cases port forwarding can be used to access them.

Get ContainerPort for the `hello` pod
```shell
CONTAINER_PORT=$(kubectl get pods --selector app=hello --output jsonpath='{.items[*].spec.containers[*].ports[*].containerPort}')
```

Forward a LocalPort of your own choice (e.g. `9000`) to a pod's ContainerPort
```shell
kubectl port-forward deployment/hello 9000:$CONTAINER_PORT
```

Hit the `hello` pod
```shell
curl "http://localhost:9000/v1/echo"
```

### Access pod B from another pod A

Get a shell to the `hello` pod
```shell
kubectl exec --stdin --tty deployment/hello -- /bin/bash
```

Hit `whoami` pod
```shell
# when pod B is in the same namespace as pod A
# curl "http://<service-name>/some/path"
curl "http://whoami/"

# when pod B is NOT in the same namespace as pod A
# curl "<service-name>.<namespace-name>.svc.cluster.local/some/path"
curl "http://whoami.apps.svc.cluster.local/"
```

### Access host resources from a pod

Get a shell to the `hello` pod
```shell
kubectl exec --stdin --tty deployment/hello -- /bin/bash
```

Hit a resource running on host (your machine) on port `9000`
```shell
curl "host.k3d.internal:9000/"
```

> Note: The host must have a running resource. Run `whoami` with `docker run -p
> 9000:9000 traefik/whoami --port 9000`

### Logs

```shell
# show snapshot logs from a deployment named hello
kubectl logs deployment/helloGet a shell to the `hello` pod

# show snapshot logs in pods defined by label app=hello
kubectl logs --selector app=hello

# stream logs from the ingres-controller pod
POD_NAME=$(kubectl get pods --namespace ingress-nginx --selector app.kubernetes.io/component=controller --output jsonpath='{.items[*].metadata.name}')
kubectl logs $POD_NAME --namespace ingress-nginx --follow

# stream logs
kubectl logs --selector app=hello --follow

# show only the most recent 20 lines of logs
kubectl logs --selector app=hello --tail=20

# show logs written in the last minute
kubectl logs --selector app=hello --since=1m

# for more examples
kubectl logs --help
```



- [Flux CLI](https://fluxcd.io/flux/cmd/) a continuous delivery tool that keeps Kubernetes clusters in sync




Install Flux into the cluster
```shell
flux install

flux install --registry=registry.localhost:5000

flux install \
  --components=source-controller,kustomize-controller \
  --registry=docker.io/fluxcd
```

Create a git source
```shell
flux create source git flux-system \
  --url=https://github.com/MousaZeidBaker/lk8s \
  --branch=feat/flux \
  --interval=1m0s
```

Create a bucket source
```shell
flux create source bucket lk8s-bucket \
  --bucket-name=lk8s-bucket \
  --endpoint=minio.apps.svc.cluster.local:9000 \
  --insecure=true \
  --access-key=minioadmin \
  --secret-key=minioadmin \
  --interval=10m
```

Create a Kustomization resource
```shell
flux create kustomization lk8s \
  --source=Bucket/lk8s-bucket \
  --path="./clusters/prod" \
  --prune=true \
  --interval=1m0s
```

Get all resources and statuses
```shell
flux get all --all-namespaces
```

Triggering a reconcile
```shell
kubectl annotate \
  --field-manager=flux-client-side-apply \
  --overwrite  bucket/lk8s-bucket reconcile.fluxcd.io/requestedAt="$(date +%s)" \
  --namespace flux-system
```

Wait for `kustomization/infrastructure` to be ready
```shell
kubectl wait kustomization/infrastructure \
  --for=condition=ready \
  --timeout=2m \
  --namespace flux-system
```

Delete all resources in the `apps` namespace
```shell
kubectl delete all --all --namespace apps
```

Create Docker network
```shell
docker network create minio
```

Start minio server
```shell
docker run \
  --network=minio \
  --name minio \
  --user $(id -u):$(id -g) \
  -p 9000:9000 \
  -p 9090:9090 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v $PWD/volumes/storage/minio:/data \
  quay.io/minio/minio server /data --console-address ":9090"
```

Use minio client `mc` to create a bucket and copy related files to it
```shell
docker run \
  --net=minio \
  --entrypoint=/bin/sh \
  -v $PWD/apps:/apps \
  -v $PWD/clusters:/clusters \
  -v $PWD/infrastructure:/infrastructure \
  minio/mc \
  -c "mc config host add minio http://minio:9000 minioadmin minioadmin \
    && mc mb --with-versioning --ignore-existing minio/lk8s-bucket \
    && mc cp --recursive ./apps ./clusters ./infrastructure minio/lk8s-bucket \
    && mc ls minio"
```
