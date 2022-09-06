# Kubernetes Job to collect and export pods metrics

```bash

docker image build -t juliocesarmidia/kube-pod-metrics-collector:latest .


# without send to cloudwatch
docker container run --rm -d \
  --name pod-metrics \
  --restart 'no' \
  --network host \
  -e RUNNING_IN_KUBERNETES='0' \
  -e SCHEDULE_SECONDS_INTERVAL='60' \
  -e PENDING_MINS_TO_BE_CRASHED='5' \
  -e IGNORE_NAMESPACES='kube-system,kube-public,kube-node-lease' \
  -e SEND_TO_CLOUDWATCH='0' \
  -e KUBECONFIG='/root/.kube/config' \
  -e KUBECONTEXT='kubernetes-admin@kubernetes' \
  -v /root/.kube/config:/root/.kube/config \
  juliocesarmidia/kube-pod-metrics-collector:latest

docker stats pod-metrics

# sending to cloudwatch
export AWS_ACCESS_KEY_ID="AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="AWS_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"

docker container run --rm -d \
  --name pod-metrics \
  --restart 'no' \
  --network host \
  -e RUNNING_IN_KUBERNETES='0' \
  -e SCHEDULE_SECONDS_INTERVAL='60' \
  -e PENDING_MINS_TO_BE_CRASHED='5' \
  -e IGNORE_NAMESPACES='kube-system,kube-public,kube-node-lease' \
  -e SEND_TO_CLOUDWATCH='1' \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION \
  -e KUBECONFIG='/root/.kube/config' \
  -e KUBECONTEXT='kubernetes-admin@kubernetes' \
  -v /root/.kube/config:/root/.kube/config \
  juliocesarmidia/kube-pod-metrics-collector:latest

docker container logs -f pod-metrics

docker container rm -f pod-metrics



kubectl run alpine -n default \
  --restart Always \
  --image alpine:null \
  sleep infinity --dry-run -o yaml

kubectl run alpine -n default \
  --restart Always \
  --image alpine:null \
  sleep infinity

kubectl delete pod/alpine -n default



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

kubectl get secret/pod-metrics-secrets -n default

kubectl delete secret/pod-metrics-secrets -n default


kubectl apply -f pod.yaml

kubectl get pod -l app=pod-metrics -n default
kubectl top pod -l app=pod-metrics -n default


kubectl logs -f -l app=pod-metrics -n default --tail 100

kubectl logs -l app=pod-metrics -n default --tail 1000


kubectl exec -it pod/pod-metrics -n default -- sh

API_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
API_SERVER="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT_HTTPS}"

curl \
  --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $API_TOKEN" \
  --url "${API_SERVER}/api"


kubectl delete -f pod.yaml

```
