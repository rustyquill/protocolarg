#
# create an iam user with secret access key
# which can execute the deployments for the oiar website
# the user is then used by the oiar-website github action
#

resource "aws_iam_user" "grafana" {
  name = "grafana"
}

resource "aws_iam_access_key" "grafana" {
  user = aws_iam_user.grafana.name
}

resource "aws_iam_policy" "grafana" {
  policy = data.aws_iam_policy_document.grafana.json

}


resource "aws_iam_user_policy_attachment" "grafana" {
  user = aws_iam_user.grafana.name
  policy_arn = aws_iam_policy.grafana.arn
}



# https://grafana.com/docs/grafana/latest/datasources/aws-cloudwatch/
data "aws_iam_policy_document" "grafana" {
  statement {
    actions = [
        "cloudwatch:DescribeAlarmsForMetric",
        "cloudwatch:DescribeAlarmHistory",
        "cloudwatch:DescribeAlarms",
        "cloudwatch:ListMetrics",
        "cloudwatch:GetMetricData",
        "cloudwatch:GetInsightRuleReport",
    ]

    resources = ["*"]
  }
  statement {
    actions = [
        "logs:DescribeLogGroups",
        "logs:GetLogGroupFields",
        "logs:StartQuery",
        "logs:StopQuery",
        "logs:GetQueryResults",
        "logs:GetLogEvents",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
        "ec2:DescribeTags",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
        "tag:GetResources",
    ]
    resources = ["*"]
  }
}


#
# output the secrets to push to the github action
#

output "grafana_access_key_id" {
  value = aws_iam_access_key.grafana.id
}

output "grafana_access_key_secret" {
  value = aws_iam_access_key.grafana.secret
  sensitive = true
}




