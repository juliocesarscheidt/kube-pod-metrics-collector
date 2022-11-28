<div align="center">
  # Kube Pod Metrics Collector <img src="https://raw.githubusercontent.com/juliocesarscheidt/kube-pod-metrics-collector/main/images/logo.png" alt="Logo" height="40px"/>
</div>

<div align="center">
  <a href="https://github.com/juliocesarscheidt/kube-pod-metrics-collector/blob/main/LICENSE">
    <img alt="GitHub License" src="https://img.shields.io/github/license/juliocesarscheidt/kube-pod-metrics-collector?logo=GitHub&style=flat-square">
  </a>
  <a href="https://hub.docker.com/r/juliocesarscheidt/kube-pod-metrics-collector">
    <img alt="Docker pulls" src="https://img.shields.io/docker/pulls/juliocesarmidia/kube-pod-metrics-collector?color=%23099cec&logo=Docker&style=flat-square">
  </a>
  <a href="https://hub.docker.com/r/juliocesarscheidt/kube-pod-metrics-collector">
    <img alt="Image size" src="https://img.shields.io/docker/image-size/juliocesarmidia/kube-pod-metrics-collector/latest?logo=Docker&style=flat-square">
  </a>
</div>

<hr>

We are using the Kubernetes API to retrieve all the pods, then we iterate over them to check their statuses, and when the pod is failed, or pending for more than X minutes (the "X" minutes is an option passed through variable), we increment our metric of crashed pods by namespace, to send it later to CloudWatch as a custom metric where we could better analyse the information and create some alerts on it.

When running as a pod inside a Kubernetes cluster, we are going to use a service account, that it will give a bearer token to call the Kubernetes API in a transparent fashion.

When running as a container it is required to pass a kubeconfig file to interact with some cluster.

## Prerequisites

- The Kubernetes API used must be accessible from the location where this pod/container is running.

- In order to send metrics to CloudWatch it is required an user with credentials for that, more instructions on how to create this user here: [Create CloudWatch User](./cloudwatch-user.md)

## Instructions

> Running as container

```bash
# build image
docker image build -t docker.io/juliocesarmidia/kube-pod-metrics-collector:v1.0.0 ./src

# or pull from docker hub
docker image pull docker.io/juliocesarmidia/kube-pod-metrics-collector:v1.0.0

# run without sending metrics to CloudWatch - dry run
docker container run --rm -d \
  --name pod-metrics \
  --restart 'no' \
  --network host \
  -e RUNNING_IN_KUBERNETES='0' \
  -e SCHEDULE_SECONDS_INTERVAL='60' \
  -e PENDING_MINS_TO_BE_CRASHED='1' \
  -e IGNORE_NAMESPACES='kube-public,kube-node-lease' \
  -e SEND_TO_CLOUDWATCH='0' \
  -e KUBECONFIG='/root/.kube/config' \
  -e KUBECONTEXT=$(kubectl config current-context) \
  -v $HOME/.kube/config:/root/.kube/config \
  docker.io/juliocesarmidia/kube-pod-metrics-collector:v1.0.0

# logs and stats
docker container logs -f pod-metrics
docker stats pod-metrics

# run sending metrics to CloudWatch (it requires AWS credentials)
docker container run --rm -d \
  --name pod-metrics \
  --restart 'no' \
  --network host \
  -e RUNNING_IN_KUBERNETES='0' \
  -e SCHEDULE_SECONDS_INTERVAL='60' \
  -e PENDING_MINS_TO_BE_CRASHED='1' \
  -e IGNORE_NAMESPACES='kube-public,kube-node-lease' \
  -e SEND_TO_CLOUDWATCH='1' \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION \
  -e KUBECONFIG='/root/.kube/config' \
  -e KUBECONTEXT=$(kubectl config current-context) \
  -v $HOME/.kube/config:/root/.kube/config \
  docker.io/juliocesarmidia/kube-pod-metrics-collector:v1.0.0

# clean up
docker container rm -f pod-metrics
```

> Running inside Kubernetes as pod

```bash
# create a secret for CloudWatch sdk usage, with the AWS credentials
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: pod-metrics-secrets
  namespace: default
data:
  AWS_ACCESS_KEY_ID: "$(echo -n "$AWS_ACCESS_KEY_ID" | base64 -w0)"
  AWS_SECRET_ACCESS_KEY: "$(echo -n "$AWS_SECRET_ACCESS_KEY" | base64 -w0)"
  AWS_DEFAULT_REGION: "$(echo -n "$AWS_DEFAULT_REGION" | base64 -w0)"
EOF

export CLUSTER_NAME=$(kubectl config current-context)

# create a configmap for CloudWatch sdk usage, with the cluster name
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: pod-metrics-configmap
  namespace: default
data:
  CLUSTER_NAME: "$CLUSTER_NAME"
EOF

# check secret and cm
kubectl get secret/pod-metrics-secrets -n default -o yaml
kubectl get configmap/pod-metrics-configmap -n default -o yaml

# create the pod
kubectl apply -f deployment.yaml

# check pod execution
kubectl get pod -l app=pod-metrics -n default
kubectl describe pod -l app=pod-metrics -n default
kubectl top pod -l app=pod-metrics -n default

# see logs
kubectl logs -f -l app=pod-metrics -n default --tail 1000 --timestamps
kubectl logs -f deploy/pod-metrics -n default --tail 1000 -c pod-metrics --timestamps

# command to execute "sh" inside the pod
kubectl exec -it pod/pod-metrics -n default -- sh

# calling the Kubernetes API inside the pod
API_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
API_SERVER="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT_HTTPS}"

curl \
  --cacert '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $API_TOKEN" \
  --url "${API_SERVER}/api"

# clean up
kubectl delete -f deployment.yaml
kubectl delete secret/pod-metrics-secrets -n default
kubectl delete configmap/pod-metrics-configmap -n default
```
