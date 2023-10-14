#
# this terraform file creates the required resources
# for our bonzo.land website hoosting
#
# thanks to:
# https://hands-on.cloud/cloudfront-terraform-examples/#h-integrating-cloudfront-with-s3-using-terraform
#

# ============
# S3 Bucket for Website content
# we create 3 different s3 buckets,
# - inactive: bucket used by cloudfront if bonzo_land_website_is_active = false
# - active: bucket used by cloudfront for "normal" website if bonzo_land_website_is_active = true
# - nightmare: bucket used by cloudfront for "nightmare" website
# ============

locals {
  bonzo_land_bucket_base = "bonzo-land-website"
  bonzo_land_buckets = {
    inactive = "${local.bonzo_land_bucket_base}-inactive"
    active = "${local.bonzo_land_bucket_base}-active"
    nightmare = "${local.bonzo_land_bucket_base}-nightmare"
  }
}

resource "aws_s3_bucket" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = each.value
}

resource "aws_s3_bucket_ownership_controls" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets
  depends_on = [aws_s3_bucket_ownership_controls.bonzo_website_buckets]

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_website_configuration" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_policy" "bonzo_website_buckets" {
  for_each = local.bonzo_land_buckets

  bucket = aws_s3_bucket.bonzo_website_buckets[each.key].id
  policy = data.aws_iam_policy_document.bonzo_website_buckets_policy_document[each.key].json
}

data "aws_iam_policy_document" "bonzo_website_buckets_policy_document" {
  for_each = local.bonzo_land_buckets

  statement {
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.bonzo_website_buckets[each.key].arn}/*"
    ]
    condition {
      test = "StringEquals"
      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.bonzo_website.arn
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

# ============
# Lambda for origin request to display "nightmare" mode lambda
# ============

data "aws_iam_policy_document" "bonzoland_nightmare_lambda" {
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

resource "aws_iam_role" "bonzoland_nightmare_lambda" {
    provider = aws.us-east-1

    assume_role_policy = data.aws_iam_policy_document.bonzoland_nightmare_lambda.json
}

resource "aws_iam_role_policy_attachment" "bonzoland_nightmare_lambda" {
    provider = aws.us-east-1

    role       = aws_iam_role.bonzoland_nightmare_lambda.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_s3_object" "bonzoland_nightmare_lambda" {
  provider = aws.us-east-1

  bucket = aws_s3_bucket.lambda_package_us_east_1.bucket
  key    = "nightmare.zip"
}

resource "aws_lambda_function" "bonzoland_nightmare_lambda" {
    provider = aws.us-east-1

    function_name = "bonzoland-nightmare"

    s3_bucket         = data.aws_s3_object.bonzoland_nightmare_lambda.bucket
    s3_key            = data.aws_s3_object.bonzoland_nightmare_lambda.key
    s3_object_version = data.aws_s3_object.bonzoland_nightmare_lambda.version_id

    handler = "handler.lambda_handler"
    runtime = "python3.9"

    publish = true # enable versioning for lambda@edge

    role = aws_iam_role.bonzoland_nightmare_lambda.arn

    timeout = 3
    memory_size = 128
}

# ============
# S3 Bucket for Cloudfront Access Logs
# ============

resource "aws_s3_bucket" "bonzo_website_access_logs" {
    bucket = "bonzo-static-website-access-logs"
}

resource "aws_s3_bucket_ownership_controls" "bonzo_website_access_logs" {
  bucket = aws_s3_bucket.bonzo_website_access_logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "bonzo_website_access_logs" {
  depends_on = [aws_s3_bucket_ownership_controls.bonzo_website_access_logs]

  bucket = aws_s3_bucket.bonzo_website_access_logs.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "bonzo_website_access_logs" {
  bucket = aws_s3_bucket.bonzo_website_access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bonzo_website_access_logs" {
  bucket = aws_s3_bucket.bonzo_website_access_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "bonzo_website_access_logs" {
  bucket = aws_s3_bucket.bonzo_website_access_logs.id
  versioning_configuration {
    status = "Disabled"
  }
}

# ============
# Cloudfront ACM certificate
# ============

resource "aws_acm_certificate" "bonzo_website_certificate" {
  provider = aws.us-east-1

  domain_name               = local.domain_names.bonzoland
  subject_alternative_names = ["*.${local.domain_names.bonzoland}"]
  validation_method         = "DNS"
}


resource "aws_route53_record" "bonzo_website_certificate_validation" {
  provider = aws.us-east-1

  for_each = {
    for d in aws_acm_certificate.bonzo_website_certificate.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.bonzoland.zone_id
}

resource "aws_acm_certificate_validation" "bonzo_website_certificate_validation" {
  provider = aws.us-east-1

  certificate_arn         = aws_acm_certificate.bonzo_website_certificate.arn
  validation_record_fqdns = [for r in aws_route53_record.bonzo_website_certificate_validation : r.fqdn]
}

# ============
# Cloudfront Distribution
# ============

locals {
  # define origin depending on bonzo_land_website_is_active
  bonzo_land_active_origin_id = local.bonzo_land_website_is_active ? aws_s3_bucket.bonzo_website_buckets["active"].id : aws_s3_bucket.bonzo_website_buckets["inactive"].id
  bonzo_land_active_terms_and_conditions_viewer_request = local.bonzo_land_website_is_active ? [1] : []
  bonzo_land_active_nightmare_mode = local.bonzo_land_website_is_active && local.bonzo_land_nightmare_mode_is_active ? [1] : []

}

resource "aws_cloudfront_origin_access_control" "bonzo_website" {
  name                              = "bonzo-land-website"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "bonzo_website" {
  enabled             = true

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.bonzo_website_access_logs.bucket_domain_name
    prefix          = "cloudfront"
  }

  aliases             = [
    local.domain_names.bonzoland,
    "www.${local.domain_names.bonzoland}"
  ]

  default_root_object = "index.html"

  # "active" website
  origin {
    origin_id                = aws_s3_bucket.bonzo_website_buckets["active"].id
    domain_name              = aws_s3_bucket.bonzo_website_buckets["active"].bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.bonzo_website.id
  }

  # "inactive" website
  origin {
    origin_id                = aws_s3_bucket.bonzo_website_buckets["inactive"].id
    domain_name              = aws_s3_bucket.bonzo_website_buckets["inactive"].bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.bonzo_website.id
  }

  # "nightmare" website
  origin {
    origin_id                = aws_s3_bucket.bonzo_website_buckets["nightmare"].id
    domain_name              = aws_s3_bucket.bonzo_website_buckets["nightmare"].bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.bonzo_website.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }

  default_cache_behavior {
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.bonzo_land_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"

    dynamic "lambda_function_association" {
      for_each = local.bonzo_land_active_terms_and_conditions_viewer_request
      content {
        event_type   = "viewer-request"
        lambda_arn   = aws_lambda_function.terms_and_conditions_request_lambda.qualified_arn
        include_body = false
      }
    }

    dynamic "lambda_function_association" {
      for_each = local.bonzo_land_active_nightmare_mode
      content {
        event_type   = "origin-request"
        lambda_arn   = aws_lambda_function.bonzoland_nightmare_lambda.qualified_arn
        include_body = false
      }
    }
  }

  ordered_cache_behavior {
    path_pattern             = "/favicon.ico"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.bonzo_land_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/robots.txt"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.bonzo_land_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.bonzo_website_certificate.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2018"
  }

    custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 404
    response_code         = 404
    response_page_path    = "/404.html"
  }

  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 403
    response_code         = 403
    response_page_path    = "/404.html"
  }

  price_class = "PriceClass_100" # us and europe
}


resource "aws_route53_record" "bonzo_website" {
  name    = local.domain_names.bonzoland
  zone_id = aws_route53_zone.bonzoland.zone_id
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.bonzo_website.domain_name
    zone_id                = aws_cloudfront_distribution.bonzo_website.hosted_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "bonzo_website_www" {
  name    = "www.${local.domain_names.bonzoland}"
  zone_id = aws_route53_zone.bonzoland.zone_id
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.bonzo_website.domain_name
    zone_id                = aws_cloudfront_distribution.bonzo_website.hosted_zone_id
    evaluate_target_health = true
  }
}

