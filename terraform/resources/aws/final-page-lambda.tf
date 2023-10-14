# ============
# Lambda for viewer request to verify terms and conditions
# cookie or redirect
# ============

data "aws_iam_policy_document" "final_page_lambda" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = [
        "edgelambda.amazonaws.com",
        "lambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "final_page_lambda" {
    provider = aws.us-east-1

    assume_role_policy = data.aws_iam_policy_document.final_page_lambda.json
}

resource "aws_iam_role_policy_attachment" "final_page_lambda" {
    provider = aws.us-east-1

    role       = aws_iam_role.final_page_lambda.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_s3_object" "final_page_lambda" {
  provider = aws.us-east-1

  bucket = aws_s3_bucket.lambda_package_us_east_1.bucket
  key    = "final-page.zip"
}

resource "aws_lambda_function" "final_page_lambda" {
    provider = aws.us-east-1

    function_name = "final-page"

    s3_bucket         = data.aws_s3_object.final_page_lambda.bucket
    s3_key            = data.aws_s3_object.final_page_lambda.key
    s3_object_version = data.aws_s3_object.final_page_lambda.version_id

    handler = "handler.lambda_handler"
    runtime = "python3.9"

    publish = true # enable versioning for lambda@edge

    role = aws_iam_role.final_page_lambda.arn

    timeout = 3
    memory_size = 128
}
