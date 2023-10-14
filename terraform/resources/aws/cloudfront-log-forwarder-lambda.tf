#
# create cloudwatch log groups, iam policies
# and multiple lambdas to stream access logs from cloudfront to cloudwatch
#

locals {
    cloudfront_access_logs_buckets = {
        "${aws_s3_bucket.static_website_access_logs.bucket}" = { "enabled" = local.cloudwatch_log_stream_enabled.oiar, "arn" = aws_s3_bucket.static_website_access_logs.arn }
        "${aws_s3_bucket.bonzo_website_access_logs.bucket}" = { "enabled" = local.cloudwatch_log_stream_enabled.bonzoland, "arn" = aws_s3_bucket.bonzo_website_access_logs.arn }
        "${aws_s3_bucket.bonzobazaar_website_access_logs.bucket}" = { "enabled" = local.cloudwatch_log_stream_enabled.bonzobazaar, "arn" = aws_s3_bucket.bonzobazaar_website_access_logs.arn }
        "${aws_s3_bucket.magnusprotocolarg_website_access_logs.bucket}" = { "enabled" = local.cloudwatch_log_stream_enabled.magnusprotocolarg, "arn" = aws_s3_bucket.magnusprotocolarg_website_access_logs.arn }
        "${aws_s3_bucket.themagnusinstitute_website_access_logs.bucket}" = { "enabled" = local.cloudwatch_log_stream_enabled.magnusinstitute, "arn" = aws_s3_bucket.themagnusinstitute_website_access_logs.arn }
        "${aws_s3_bucket.documentleak_website_access_logs.bucket}" = { "enabled" = local.cloudwatch_log_stream_enabled.freiheitentschluesseln, "arn" = aws_s3_bucket.documentleak_website_access_logs.arn }
    }

    # get all arns that are not null and add them to a list
    cloudfront_log_forwarder_s3_logs_access = [ for b, a in local.cloudfront_access_logs_buckets : "${a.arn}/*" ]

}

# ======================================================================================================================
# cloudwatch log group
# ======================================================================================================================

resource "aws_cloudwatch_log_group" "cloudfront_log_forwarde_per_bucket" {
  for_each = local.cloudfront_access_logs_buckets

  name = substr("cloudfront-forwarded-logs-${each.key}", 0, 64)
  retention_in_days = 90
}


# ======================================================================================================================
# lambda access policy
# ======================================================================================================================



data "aws_iam_policy_document" "cloudfront_log_forwarder_sts" {
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

data "aws_iam_policy_document" "cloudfront_log_forwarder" {
  statement {
    actions = [
      "s3:GetObject",
    ]

    resources = local.cloudfront_log_forwarder_s3_logs_access
  }

  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      for log_group in aws_cloudwatch_log_group.cloudfront_log_forwarde_per_bucket : log_group.arn
    ]
  }
}

resource "aws_iam_policy" "cloudfront_log_forwarder" {

  name        = "cloudfront-log-forwarder"
  policy      = data.aws_iam_policy_document.cloudfront_log_forwarder.json
}

resource "aws_iam_role" "cloudfront_log_forwarder" {
    assume_role_policy = data.aws_iam_policy_document.cloudfront_log_forwarder_sts.json
}

resource "aws_iam_role_policy_attachment" "cloudfront_log_forwarder" {
    role       = aws_iam_role.cloudfront_log_forwarder.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "cloudfront_log_forwarder_access" {
    role       = aws_iam_role.cloudfront_log_forwarder.name
    policy_arn = aws_iam_policy.cloudfront_log_forwarder.arn
}

# ======================================================================================================================
# create lambdas and lambda permissions
# ======================================================================================================================

data "aws_s3_object" "cloudfront_log_forwarder" {
  bucket = aws_s3_bucket.lambda_package_eu_west_2.bucket
  key    = "cloudfront-log-forwarder.zip"
}

resource "aws_lambda_function" "cloudfront_log_forwarder" {
    for_each = local.cloudfront_access_logs_buckets

    function_name = substr("cloudfront-log-forwarder-${each.key}", 0, 64)

    s3_bucket         = data.aws_s3_object.cloudfront_log_forwarder.bucket
    s3_key            = data.aws_s3_object.cloudfront_log_forwarder.key
    s3_object_version = data.aws_s3_object.cloudfront_log_forwarder.version_id

    handler = "handler.lambda_handler"
    runtime = "python3.8"

    role = aws_iam_role.cloudfront_log_forwarder.arn

    environment {
        variables = {
            LOG_GROUP_NAME = aws_cloudwatch_log_group.cloudfront_log_forwarde_per_bucket[each.key].name
            LOG_STREAM_NAME = each.key
        }
    }

    timeout = 300
    memory_size = 128
}

resource "aws_lambda_permission" "cloudfront_log_forwarder" {
    for_each = local.cloudfront_access_logs_buckets

    function_name = aws_lambda_function.cloudfront_log_forwarder[each.key].arn
    action        = "lambda:InvokeFunction"

    principal  = "s3.amazonaws.com"
    source_arn = each.value.arn
}

# ======================================================================================================================
# create event to stream new logs
# ======================================================================================================================

locals {
  # ensure we create a filtered list of buckets that have a log forwarder
  cloudfront_access_logs_buckets_with_forwarder_enabled = {
    for b, a in local.cloudfront_access_logs_buckets : b => a if a.enabled
  }
}

resource "aws_s3_bucket_notification" "cloudfront_log_forwarder" {
    for_each = local.cloudfront_access_logs_buckets_with_forwarder_enabled

    bucket = each.key

  lambda_function {
    lambda_function_arn = aws_lambda_function.cloudfront_log_forwarder[each.key].arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.cloudfront_log_forwarder]
}
