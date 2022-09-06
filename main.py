import schedule

from datetime import datetime, timezone

from kubernetes_client import (
  get_kube_client,
  get_cluster_name,
  list_pods,
  list_namespaces
)
from cloudwatch_client import (
  get_send_to_cloudwatch,
  get_cloudwatch_metric_name,
  get_cloudwatch_metric_namespace,
  get_client_cloudwatch,
  put_metrics
)
from config import (
  get_schedule_seconds_interval,
  get_pending_minutes_to_be_crashed,
  get_ignore_namespaces
)

def main():
  ignore_namespaces = get_ignore_namespaces()
  pending_minutes_to_be_crashed = get_pending_minutes_to_be_crashed()
  send_to_cloudwatch = get_send_to_cloudwatch()
  cloudwatch_metric_name = get_cloudwatch_metric_name()
  cloudwatch_metric_namespace = get_cloudwatch_metric_namespace()

  api_v1 = get_kube_client()
  if send_to_cloudwatch == True:
    client_cloudwatch = get_client_cloudwatch()

  cluster_name = get_cluster_name()
  print('cluster_name', cluster_name)

  now = datetime.utcnow()
  now = now.replace(tzinfo=timezone.utc)

  print(now)
  print('now', now.isoformat())

  crashed_pods = {}

  namespaces = list_namespaces(api_v1)
  for ns in namespaces:
    ns_name = ns.metadata.name
    ns_name = ns_name[0].upper() + ns_name[1:].lower()
    if ns.status.phase == 'Active' and not ns_name in crashed_pods:
      if len(ignore_namespaces) <= 0 or not ns.metadata.name in ignore_namespaces:
        crashed_pods[ns_name] = {'count': 0, 'pods': []}

  pods = list_pods(api_v1)

  for pod in pods:
    if len(ignore_namespaces) > 0 and pod.metadata.namespace in ignore_namespaces:
      # Ignoring Namespace
      continue

    ns = pod.metadata.namespace
    ns = ns[0].upper() + ns[1:].lower()

    # https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
    # ['Pending', 'Running', 'Succeeded', 'Failed', 'Unknown']
    if pod.status.phase == 'Pending':
      pod.status.start_time = pod.status.start_time.replace(tzinfo=timezone.utc)

      print('Pod Name {} :: Pod IP {} :: Pod Phase {} :: Pod Start Time {} :: Host IP {} :: Pod Namespace'
        .format(pod.metadata.name, pod.status.pod_ip, pod.status.phase,
        pod.status.start_time.isoformat(), pod.status.host_ip, ns))

      diff = (now - pod.status.start_time)
      diff_in_secs = diff.total_seconds()
      print('diff_in_secs', diff_in_secs)
      diff_in_mins = (diff_in_secs / 60)
      print('diff_in_mins', diff_in_mins)

      if diff_in_mins > pending_minutes_to_be_crashed:
        crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
        crashed_pods[ns]['pods'].append(pod.metadata.name)

    elif pod.status.phase == 'Failed' or pod.status.phase == 'Unknown':
      pod.status.start_time = pod.status.start_time.replace(tzinfo=timezone.utc)
      print('pod.status.start_time', pod.status.start_time.isoformat())

      print('Pod Name {} :: Pod IP {} :: Pod Phase {} :: Pod Start Time {} :: Host IP {} :: Pod Namespace'
        .format(pod.metadata.name, pod.status.pod_ip, pod.status.phase,
        pod.status.start_time.isoformat(), pod.status.host_ip, ns))

      crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
      crashed_pods[ns]['pods'].append(pod.metadata.name)

  for ns in crashed_pods.keys():
    print('ns', ns, crashed_pods[ns])
    if send_to_cloudwatch == True:
      dimensions = [{
        'Name': 'Namespace',
        'Value': ns
      }, {
        'Name': 'ClusterName',
        'Value': cluster_name
      }]
      put_metrics(client_cloudwatch, cloudwatch_metric_name,
                  cloudwatch_metric_namespace, dimensions,
                  'Count', crashed_pods[ns]['count'])
      print('Sent to cloudwatch', ns)

if __name__ == '__main__':
  main()

  schedule_seconds_interval = get_schedule_seconds_interval()
  print('Running every {} seconds'.format(schedule_seconds_interval))

  schedule.every(schedule_seconds_interval).seconds.do(main)
  while True:
    schedule.run_pending()
