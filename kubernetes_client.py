import os

from kubernetes import client, config
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

from config import get_running_in_kubernetes

def get_kubernetes_variables():
  KUBERNETES_SERVICE_HOST = os.environ.get('KUBERNETES_SERVICE_HOST')
  KUBERNETES_SERVICE_PORT_HTTPS = os.environ.get('KUBERNETES_SERVICE_PORT_HTTPS')

  with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
    api_token = file.read()

  api_ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
  api_server = f'https://{KUBERNETES_SERVICE_HOST}:{KUBERNETES_SERVICE_PORT_HTTPS}'

  return api_token, api_ca_cert, api_server

def get_kube_client():
  running_in_kubernetes = get_running_in_kubernetes()

  if running_in_kubernetes == True:
    api_token, api_ca_cert, api_server = get_kubernetes_variables()
    configuration = client.Configuration()
    configuration.host = api_server
    configuration.api_key = {'authorization': 'Bearer ' + api_token}
    configuration.ssl_ca_cert = api_ca_cert
    configuration.verify_ssl = True
  else:
    configuration = config.load_kube_config(
      config_file = os.environ.get('KUBECONFIG', '~/.kube/config'),
      context = os.environ.get('KUBECONTEXT', ''),
    )

  api_v1 = client.CoreV1Api(client.ApiClient(configuration))
  return api_v1

def list_pods(api_v1, watch=False):
  try:
    for attempt in Retrying(
      stop=stop_after_attempt(3),
      wait=wait_exponential()
    ):
      with attempt:
        pods = api_v1.list_pod_for_all_namespaces(watch=watch)
        return pods.items

  except RetryError as e:
    print(e)

  except Exception as e:
    print(e)

def list_namespaces(api_v1, watch=False):
  try:
    for attempt in Retrying(
      stop=stop_after_attempt(3),
      wait=wait_exponential()
    ):
      with attempt:
        namespaces = api_v1.list_namespace(watch=watch)
        return namespaces.items

  except RetryError as e:
    print(e)

  except Exception as e:
    print(e)
