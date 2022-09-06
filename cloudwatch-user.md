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
echo "${CREDENTIALS}" | jq -r '.AccessKey'

export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws iam attach-user-policy \
  --user-name "put-metric-data-user" \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/put-metric-data-policy"

export AWS_ACCESS_KEY_ID="$(echo "${CREDENTIALS}" | jq -r '.AccessKey.AccessKeyId')"
export AWS_SECRET_ACCESS_KEY="$(echo "${CREDENTIALS}" | jq -r '.AccessKey.SecretAccessKey')"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"


# clean up
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION

aws iam detach-user-policy \
  --user-name "put-metric-data-user" \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/put-metric-data-policy"

aws iam delete-policy \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/put-metric-data-policy"

aws iam delete-access-key --access-key-id "$(echo "${CREDENTIALS}" | jq -r '.AccessKey.AccessKeyId')"

aws iam delete-user --user-name "put-metric-data-user"

```
