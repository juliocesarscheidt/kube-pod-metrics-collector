import os

def get_running_in_kubernetes():
  # RUNNING_IN_KUBERNETES => 1 or 0
  RUNNING_IN_KUBERNETES = bool(int(os.environ.get('RUNNING_IN_KUBERNETES', '0')))
  print('RUNNING_IN_KUBERNETES', RUNNING_IN_KUBERNETES)
  return RUNNING_IN_KUBERNETES

def get_schedule_seconds_interval():
  # SCHEDULE_SECONDS_INTERVAL => default 60 seconds
  SCHEDULE_SECONDS_INTERVAL = int(os.environ.get('SCHEDULE_SECONDS_INTERVAL', 60))
  print('SCHEDULE_SECONDS_INTERVAL', SCHEDULE_SECONDS_INTERVAL)
  return SCHEDULE_SECONDS_INTERVAL

def get_pending_minutes_to_be_crashed():
  # PENDING_MINS_TO_BE_CRASHED => default 5 minutes
  PENDING_MINS_TO_BE_CRASHED = int(os.environ.get('PENDING_MINS_TO_BE_CRASHED', '5'))
  print('PENDING_MINS_TO_BE_CRASHED', PENDING_MINS_TO_BE_CRASHED)
  return PENDING_MINS_TO_BE_CRASHED

def get_ignore_namespaces():
  # IGNORE_NAMESPACES => e.g. kube-system,kube-public,kube-node-lease - comma-separated string
  IGNORE_NAMESPACES = os.environ.get('IGNORE_NAMESPACES', '').split(',')
  print('IGNORE_NAMESPACES', IGNORE_NAMESPACES)
  return IGNORE_NAMESPACES
