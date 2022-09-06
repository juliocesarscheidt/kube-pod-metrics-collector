

docker image build -t juliocesarmidia/kube-pod-metrics-collector:latest .

docker container run --rm -d \
  --name pod-metrics \
  --restart 'no' \
  -e RUNNING_IN_KUBERNETES='0' \
  -e SCHEDULE_SECONDS_INTERVAL='60' \
  -e PENDING_MINS_TO_BE_CRASHED='5' \
  -e IGNORE_NAMESPACES='kube-system,kube-public,kube-node-lease' \
  -e SEND_TO_CLOUDWATCH='0' \
  -e KUBECONFIG='/root/.kube/config' \
  -e KUBECONTEXT='k8s-prod-2.superdigital.vpc' \
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



kubectl apply -f pod.yaml

kubectl get secret/pod-metrics-secrets -n default


kubectl get pod -l app=pod-metrics -n default


kubectl logs -f -l app=pod-metrics -n default --tail 100

kubectl logs -l app=pod-metrics -n default --tail 1000


kubectl delete -f pod.yaml

