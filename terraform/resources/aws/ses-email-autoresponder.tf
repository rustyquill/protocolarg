
# ============
# AWS SNS Topic for email receiving, parsing and answering
# ============

resource "aws_sns_topic" "oiar_email_receiving_topic" {
  provider = aws.eu-west-1

  name = "oiar-email-receiving-topic"
}


# ============
# setup aws lambda to react on sns topic
# ============


data "aws_iam_policy_document" "oiar_sns_email" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "oiar_sns_send_email" {
  statement {
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail"
    ]

    resources = [
      "*"
    ]
  }

  # allow lambda to retrieve files from documentleak s3 bucket
  statement {
    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.documentleak_website_buckets["active"].arn}/*"
    ]
  }
}

resource "aws_iam_policy" "oiar_sns_send_email" {
  provider = aws.eu-west-1

  name        = "oiar-sns-send-email"
  policy      = data.aws_iam_policy_document.oiar_sns_send_email.json
}

resource "aws_iam_role" "oiar_sns_email_lambda" {
    provider = aws.eu-west-1

    assume_role_policy = data.aws_iam_policy_document.oiar_sns_email.json
}

resource "aws_iam_role_policy_attachment" "oiar_sns_email_lambda" {
    provider = aws.eu-west-1

    role       = aws_iam_role.oiar_sns_email_lambda.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "oiar_sns_send_email_lambda" {
    provider = aws.eu-west-1

    role       = aws_iam_role.oiar_sns_email_lambda.name
    policy_arn = aws_iam_policy.oiar_sns_send_email.arn
}

data "aws_s3_object" "oiar_sns_email_lambda" {
  provider = aws.eu-west-1

  bucket = aws_s3_bucket.lambda_package_eu_west_1.bucket
  key    = "email-autoresponder.zip"
}

resource "aws_lambda_function" "oiar_sns_email_lambda" {
    provider = aws.eu-west-1

    function_name = "oiar-sns-email"

    s3_bucket         = data.aws_s3_object.oiar_sns_email_lambda.bucket
    s3_key            = data.aws_s3_object.oiar_sns_email_lambda.key
    s3_object_version = data.aws_s3_object.oiar_sns_email_lambda.version_id

    handler = "handler.lambda_handler"
    runtime = "python3.9"

    role = aws_iam_role.oiar_sns_email_lambda.arn

    timeout = 3
    memory_size = 128

    environment {
      variables = {
        EMAIL_AUTO_RESPONDER_IS_ACTIVE = local.email_auto_responder_is_active
        EMAIL_AUTO_RESPONDER_RECIPIENTS_EXCLUSION = join(",", local.email_auto_responder_recipients_exlusion)
      }
    }
}

# subscribe lambda to topic
resource "aws_sns_topic_subscription" "oiar_sns_email_lambda" {
  provider = aws.eu-west-1
  topic_arn = aws_sns_topic.oiar_email_receiving_topic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.oiar_sns_email_lambda.arn
}

resource "aws_lambda_permission" "oiar_sns_email_lambda" {
  provider = aws.eu-west-1
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.oiar_sns_email_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.oiar_email_receiving_topic.arn
}
