import os
import boto3

def get_send_to_cloudwatch():
  # SEND_TO_CLOUDWATCH => 1 or 0
  SEND_TO_CLOUDWATCH = bool(int(os.environ.get('SEND_TO_CLOUDWATCH', '0')))
  print('SEND_TO_CLOUDWATCH', SEND_TO_CLOUDWATCH)
  return SEND_TO_CLOUDWATCH

def get_cloudwatch_metric_name():
  CLOUDWATCH_METRIC_NAME = os.environ.get(CLOUDWATCH_METRIC_NAME, 'CrashedPods')
  print('CLOUDWATCH_METRIC_NAME', CLOUDWATCH_METRIC_NAME)
  return CLOUDWATCH_METRIC_NAME

def get_cloudwatch_metric_namespace():
  CLOUDWATCH_METRIC_NAMESPACE = os.environ.get(CLOUDWATCH_METRIC_NAMESPACE, 'K8sMetrics')
  print('CLOUDWATCH_METRIC_NAMESPACE', CLOUDWATCH_METRIC_NAMESPACE)
  return CLOUDWATCH_METRIC_NAMESPACE

def get_client_cloudwatch():
  region = os.environ.get('AWS_DEFAULT_REGION', 'sa-east-1')
  print('[INFO] using region ' + region)
  client_cloudwatch = boto3.client('cloudwatch', region_name=region)
  return client_cloudwatch

def put_metrics(client_cloudwatch, metric_name, metric_namespace, dimension_name, dimension_value, unit, value):
  response = client_cloudwatch.put_metric_data(
    Namespace=metric_namespace,
    MetricData=[{
      'MetricName': metric_name,
      'Dimensions': [{
        'Name': dimension_name,
        'Value': dimension_value
      }],
      # 'Timestamp': datetime().utcnow(),
      'Value': value,
      'Unit': unit,
    }]
  )
  return response
