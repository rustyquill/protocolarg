#
# creates an s3 bucket for lambda@edge deployments
# for our websites for the ARG
#

resource "aws_s3_bucket" "lambda_package_us_east_1" {
  provider = aws.us-east-1

  bucket = "rq-arg-lambda-packages-us-east-1"
}

resource "aws_s3_bucket_versioning" "lambda_package_us_east_1" {
    provider = aws.us-east-1

    bucket = aws_s3_bucket.lambda_package_us_east_1.id
    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_ownership_controls" "lambda_package_us_east_1" {
  provider = aws.us-east-1

  bucket = aws_s3_bucket.lambda_package_us_east_1.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
resource "aws_s3_bucket_acl" "lambda_package_us_east_1" {
    provider = aws.us-east-1

    depends_on = [aws_s3_bucket_ownership_controls.lambda_package_us_east_1]

    bucket = aws_s3_bucket.lambda_package_us_east_1.id
    acl    = "private"
}

# ============
# create an s3 bucket in ireland for ses related
# lambdas
# ============

resource "aws_s3_bucket" "lambda_package_eu_west_1" {
  provider = aws.eu-west-1

  bucket = "rq-arg-lambda-packages-eu-west-1"
}

resource "aws_s3_bucket_versioning" "lambda_package_eu_west_1" {
    provider = aws.eu-west-1

    bucket = aws_s3_bucket.lambda_package_eu_west_1.id
    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_ownership_controls" "lambda_package_eu_west_1" {
  provider = aws.eu-west-1

  bucket = aws_s3_bucket.lambda_package_eu_west_1.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
resource "aws_s3_bucket_acl" "lambda_package_eu_west_1" {
    provider = aws.eu-west-1

    depends_on = [aws_s3_bucket_ownership_controls.lambda_package_eu_west_1]

    bucket = aws_s3_bucket.lambda_package_eu_west_1.id
    acl    = "private"
}

# ============
# create an s3 bucket in london for logging lambda
# ============

resource "aws_s3_bucket" "lambda_package_eu_west_2" {

  bucket = "rq-arg-lambda-packages-eu-west-2"
}

resource "aws_s3_bucket_versioning" "lambda_package_eu_west_2" {

    bucket = aws_s3_bucket.lambda_package_eu_west_2.id
    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_ownership_controls" "lambda_package_eu_west_2" {

  bucket = aws_s3_bucket.lambda_package_eu_west_2.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
resource "aws_s3_bucket_acl" "lambda_package_eu_west_2" {

    depends_on = [aws_s3_bucket_ownership_controls.lambda_package_eu_west_2]

    bucket = aws_s3_bucket.lambda_package_eu_west_2.id
    acl    = "private"
}
