#
# s3 bucket containing files for easter eggs
# currently we only have the bonzo brigage html site but who knows :-P
#


resource "aws_s3_bucket" "easter_egg_bucket" {
  bucket = "protocalarg-easter-eggs"
}

resource "aws_s3_bucket_ownership_controls" "easter_egg_bucket" {
  bucket = aws_s3_bucket.easter_egg_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "easter_egg_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.easter_egg_bucket]

  bucket = aws_s3_bucket.easter_egg_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "easter_egg_bucket" {
  bucket = aws_s3_bucket.easter_egg_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "easter_egg_bucket" {
  for_each = local.bonzobazaar_buckets

  bucket = aws_s3_bucket.easter_egg_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "easter_egg_bucket" {
  for_each = local.bonzobazaar_buckets

  bucket = aws_s3_bucket.easter_egg_bucket.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_website_configuration" "easter_egg_bucket" {
  for_each = local.bonzobazaar_buckets

  bucket = aws_s3_bucket.easter_egg_bucket.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_policy" "easter_egg_bucket" {
  for_each = local.bonzobazaar_buckets

  bucket = aws_s3_bucket.easter_egg_bucket.id
  policy = data.aws_iam_policy_document.easter_egg_bucket_policy_document[each.key].json
}

data "aws_iam_policy_document" "easter_egg_bucket_policy_document" {
  for_each = local.bonzobazaar_buckets

  statement {
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.easter_egg_bucket.arn}/*"
    ]
    condition {
      test = "StringEquals"
      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.bonzo_website.arn,
        aws_cloudfront_distribution.bonzobazaar_website.arn,
        aws_cloudfront_distribution.documentleak_website.arn,
        aws_cloudfront_distribution.ec2_forum.arn,
        aws_cloudfront_distribution.magnusprotocolarg_website.arn,
        aws_cloudfront_distribution.static_website.arn,
        aws_cloudfront_distribution.themagnusinstitute_website.arn,
      ]
    }
    principals {
      type        = "Service"
      identifiers = [
        "cloudfront.amazonaws.com"
      ]
    }
  }
}
