import os
import boto3

from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential


def get_send_to_cloudwatch():
    # SEND_TO_CLOUDWATCH => 1 or 0
    send_to_cloudwatch = bool(int(os.environ.get("SEND_TO_CLOUDWATCH", "0")))
    return send_to_cloudwatch


def get_cloudwatch_metric_name():
    cloudwatch_metric_name = os.environ.get("CLOUDWATCH_METRIC_NAME", "CrashedPods")
    return cloudwatch_metric_name


def get_cloudwatch_metric_namespace():
    cloudwatch_metric_namespace = os.environ.get(
        "CLOUDWATCH_METRIC_NAMESPACE", "K8sMetrics"
    )
    return cloudwatch_metric_namespace


def get_client_cloudwatch():
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    print("region", region)
    client_cloudwatch = boto3.client("cloudwatch", region_name=region)
    return client_cloudwatch


def put_metrics(
    client_cloudwatch, metric_name, metric_namespace, dimensions, unit, value
):
    try:
        for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential()):
            with attempt:
                response = client_cloudwatch.put_metric_data(
                    Namespace=metric_namespace,
                    MetricData=[
                        {
                            "MetricName": metric_name,
                            "Dimensions": dimensions,
                            "Unit": unit,
                            "Value": value,
                            # 'Timestamp': datetime().utcnow(),
                        }
                    ],
                )
                return response

    except RetryError as e:
        print(e)

    except Exception as e:
        print(e)
