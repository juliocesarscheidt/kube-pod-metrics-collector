import os

def get_running_in_kubernetes():
  # RUNNING_IN_KUBERNETES => 1 or 0
  running_in_kubernetes = bool(int(os.environ.get('RUNNING_IN_KUBERNETES', '0')))
  return running_in_kubernetes

def get_schedule_seconds_interval():
  # SCHEDULE_SECONDS_INTERVAL => default 60 seconds
  schedule_seconds_interval = int(os.environ.get('SCHEDULE_SECONDS_INTERVAL', '60'))
  return schedule_seconds_interval

def get_pending_minutes_to_be_crashed():
  # PENDING_MINS_TO_BE_CRASHED => default 5 minutes
  pending_minutes_to_be_crashed = int(os.environ.get('PENDING_MINS_TO_BE_CRASHED', '5'))
  return pending_minutes_to_be_crashed

def get_ignore_namespaces():
  # IGNORE_NAMESPACES => e.g. kube-system,kube-public,kube-node-lease - comma-separated string
  ignore_namespaces = os.environ.get('IGNORE_NAMESPACES', '').split(',')
  return ignore_namespaces
