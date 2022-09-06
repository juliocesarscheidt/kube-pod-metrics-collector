# Instructions on creating an AWS User to be used to interact with CloudWatch to put metric data

```bash

cat <<EOF > put_metric_data_policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["cloudwatch:PutMetricData"],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name "put-metric-data-policy" \
  --policy-document file://put_metric_data_policy.json

aws iam create-user --user-name "put-metric-data-user"

CREDENTIALS=$(aws iam create-access-key --user-name "put-metric-data-user")
echo "${CREDENTIALS}" | jq -r '.'

aws iam attach-user-policy \
  --user-name "put-metric-data-user" \
  --policy-arn "arn:aws:iam::${AWS_ACCOUNT}:policy/put-metric-data-policy"

```
