import schedule

from datetime import datetime, timezone

from kubernetes_config import get_kube_client
from cloudwatch_client import (
  get_client_cloudwatch, put_metrics, get_cloudwatch_metric_name,
  get_cloudwatch_metric_namespace
)
from config import (
  get_schedule_seconds_interval, get_pending_minutes_to_be_crashed,
  get_ignore_namespaces
)

def main():
  print('Running job')
  crashed_pods = {}

  kube_client, api_v1 = get_kube_client()
  client_cloudwatch = get_client_cloudwatch()

  now = datetime.utcnow()
  now = now.replace(tzinfo=timezone.utc)

  print(now)
  print('now', now.isoformat())

  pods = api_v1.list_pod_for_all_namespaces(watch=False)
  for pod in pods.items:
    if pod.metadata.namespace in get_ignore_namespaces():
      print('Ignoring Namespace', pod.metadata.namespace)
      continue

    ns = pod.metadata.namespace
    ns = ns[0].upper() + ns[1:].lower()

    # https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
    # ['Pending', 'Running', 'Succeeded', 'Failed', 'Unknown']
    if pod.status.phase == 'Pending':
      pod.status.start_time = pod.status.start_time.replace(tzinfo=timezone.utc)
      print('pod.status.start_time', pod.status.start_time.isoformat())

      print('Pod Name {} :: Pod IP {} :: Pod Phase {} :: Pod Start Time {} :: Host IP {} :: Pod Namespace'
        .format(pod.metadata.name, pod.status.pod_ip, pod.status.phase,
        pod.status.start_time.isoformat(), pod.status.host_ip, ns))

      diff = (now - pod.status.start_time)
      diff_in_secs = diff.total_seconds()
      print('diff_in_secs', diff_in_secs)
      diff_in_mins = (diff_in_secs / 60)
      print('diff_in_mins', diff_in_mins)

      if diff_in_mins > get_pending_minutes_to_be_crashed():
        if not ns in crashed_pods:
          crashed_pods[ns] = {'count': 0, 'pods': []}
        crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
        crashed_pods[ns]['pods'].append(pod.metadata.name)

    elif pod.status.phase == 'Failed' or pod.status.phase == 'Unknown':
      pod.status.start_time = pod.status.start_time.replace(tzinfo=timezone.utc)
      print('pod.status.start_time', pod.status.start_time.isoformat())

      print('Pod Name {} :: Pod IP {} :: Pod Phase {} :: Pod Start Time {} :: Host IP {} :: Pod Namespace'
        .format(pod.metadata.name, pod.status.pod_ip, pod.status.phase,
        pod.status.start_time.isoformat(), pod.status.host_ip, ns))

      if not ns in crashed_pods:
        crashed_pods[ns] = {'count': 0, 'pods': []}
      crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
      crashed_pods[ns]['pods'].append(pod.metadata.name)

    else: # 'Running' 'Succeeded
      if not ns in crashed_pods:
        crashed_pods[ns] = {'count': 0, 'pods': []}

  print('crashed_pods', crashed_pods)

  for ns in crashed_pods.keys():
    print('ns', ns, crashed_pods[ns])
    response = put_metrics(client_cloudwatch, get_cloudwatch_metric_name(), get_cloudwatch_metric_namespace(),
                          'Namespace', ns, 'Count', crashed_pods[ns]['count'])
    print('response', response)

if __name__ == '__main__':
  main()

  schedule_seconds_interval = get_schedule_seconds_interval()
  print('Running every {} seconds'.format(schedule_seconds_interval))

  schedule.every(schedule_seconds_interval).seconds.do(main)
  while True:
    schedule.run_pending()
