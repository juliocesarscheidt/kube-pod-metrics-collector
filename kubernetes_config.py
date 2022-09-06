import os

from kubernetes import client, config

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
  if get_running_in_kubernetes() == True:
    api_token, api_ca_cert, api_server = get_kubernetes_variables()
    configuration = client.Configuration()
    configuration.host = api_server
    configuration.api_key = {'Authorization': 'Bearer ' + api_token}
    configuration.ssl_ca_cert = api_ca_cert
    configuration.verify_ssl = True

  else:
    configuration = config.load_kube_config(
      config_file = os.environ.get('KUBECONFIG', '~/.kube/config'),
      context = os.environ.get('KUBECONTEXT', ''),
    )

  kube_client = client.ApiClient(configuration)
  api_v1 = client.CoreV1Api(kube_client)
  return kube_client, api_v1
