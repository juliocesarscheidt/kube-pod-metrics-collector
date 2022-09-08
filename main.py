import schedule

from datetime import datetime, timezone
from threading import Thread

from kubernetes_client import (
  get_kube_client,
  get_cluster_name,
  list_pods,
  list_namespaces,
  print_pod_info
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
  get_ignore_namespaces,
  get_error_statuses
)

def execute():
  ignore_namespaces = get_ignore_namespaces()
  pending_minutes_to_be_crashed = get_pending_minutes_to_be_crashed()
  send_to_cloudwatch = get_send_to_cloudwatch()
  cloudwatch_metric_name = get_cloudwatch_metric_name()
  cloudwatch_metric_namespace = get_cloudwatch_metric_namespace()
  error_statuses = get_error_statuses()

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

    # adjust timezone for start_time
    pod.status.start_time = pod.status.start_time.replace(tzinfo=timezone.utc)

    # https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
    # ['Pending', 'Running', 'Succeeded', 'Failed', 'Unknown']
    if pod.status.phase == 'Pending':
      print_pod_info(pod)

      diff = (now - pod.status.start_time)
      diff_in_secs = diff.total_seconds()
      print('diff_in_secs', diff_in_secs)
      diff_in_mins = (diff_in_secs / 60)
      print('diff_in_mins', diff_in_mins)

      # this pod is with the phase pending for more than the allowed minutes
      if diff_in_mins > pending_minutes_to_be_crashed:
        crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
        crashed_pods[ns]['pods'].append(pod.metadata.name)
        print('added to crashed pods', pod.metadata.name)

    elif pod.status.phase == 'Failed' or pod.status.phase == 'Unknown':
      print_pod_info(pod)

      crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
      crashed_pods[ns]['pods'].append(pod.metadata.name)
      print('added to crashed pods', pod.metadata.name)

    # even for Running phase, lets check if there aren't pods with failed status
    elif pod.status.phase == 'Running':
      statuses = list(pod.status.container_statuses)
      for status in statuses:
        if status.state.running is None and \
        status.state.waiting is not None and \
        status.state.waiting.reason in error_statuses:
          print_pod_info(pod)

          diff = (now - pod.status.start_time)
          diff_in_secs = diff.total_seconds()
          print('diff_in_secs', diff_in_secs)
          diff_in_mins = (diff_in_secs / 60)
          print('diff_in_mins', diff_in_mins)

          # this pod is with the status waiting for more than the allowed minutes
          if diff_in_mins > pending_minutes_to_be_crashed:
            crashed_pods[ns]['count'] = crashed_pods[ns]['count'] + 1
            crashed_pods[ns]['pods'].append(pod.metadata.name)
            print('added to crashed pods', pod.metadata.name)

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

def main():
  threads = []
  threads.append(Thread(target=execute, args=[]))
  for t in threads:
    t.start()

if __name__ == '__main__':
  main()

  schedule_seconds_interval = get_schedule_seconds_interval()
  print('Running every {} seconds'.format(schedule_seconds_interval))

  schedule.every(schedule_seconds_interval).seconds.do(main)
  while True:
    schedule.run_pending()
