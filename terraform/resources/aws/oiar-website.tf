#
# this terraform file creates the required resources
# for our static website hosting for the oiar website
#
# thanks to:
# https://hands-on.cloud/cloudfront-terraform-examples/#h-integrating-cloudfront-with-s3-using-terraform
#

# ============
# S3 Bucket for Website content
# we create 2 different s3 buckets,
# - inactive: bucket used by cloudfront if oiar_website_is_active = false
# - active: bucket used by cloudfront for "normal" website if bonzo_land_is_active = true
# ============

locals {
  oiar_website_bucket_base = "oiar-website"
  oiar_buckets = {
    inactive = "${local.oiar_website_bucket_base}-inactive"
    active = "${local.oiar_website_bucket_base}-active"
  }
}

resource "aws_s3_bucket" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = each.value
}

resource "aws_s3_bucket_ownership_controls" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "oiar_website_buckets" {
  for_each = local.oiar_buckets
  depends_on = [aws_s3_bucket_ownership_controls.oiar_website_buckets]

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_website_configuration" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_policy" "oiar_website_buckets" {
  for_each = local.oiar_buckets

  bucket = aws_s3_bucket.oiar_website_buckets[each.key].id
  policy = data.aws_iam_policy_document.oiar_website_buckets_policy_document[each.key].json
}

data "aws_iam_policy_document" "oiar_website_buckets_policy_document" {
  for_each = local.oiar_buckets

  statement {
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.oiar_website_buckets[each.key].arn}/*"
    ]
    condition {
      test = "StringEquals"
      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.static_website.arn
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
# S3 Bucket for Cloudfront Access Logs
# ============

resource "aws_s3_bucket" "static_website_access_logs" {
    bucket = "oiar-static-website-access-logs"
}

resource "aws_s3_bucket_ownership_controls" "static_website_access_logs" {
  bucket = aws_s3_bucket.static_website_access_logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "static_website_access_logs" {
  depends_on = [aws_s3_bucket_ownership_controls.static_website_access_logs]

  bucket = aws_s3_bucket.static_website_access_logs.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "static_website_access_logs" {
  bucket = aws_s3_bucket.static_website_access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static_website_access_logs" {
  bucket = aws_s3_bucket.static_website_access_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "static_website_access_logs" {
  bucket = aws_s3_bucket.static_website_access_logs.id
  versioning_configuration {
    status = "Disabled"
  }
}


# ============
# Cloudfront ACM certificate
# ============

resource "aws_acm_certificate" "static_website_certificate" {
  provider = aws.us-east-1

  domain_name               = local.domain_names.oiar
  subject_alternative_names = ["*.${local.domain_names.oiar}"]
  validation_method         = "DNS"
}


resource "aws_route53_record" "static_website_certificate_validation" {
  provider = aws.us-east-1

  for_each = {
    for d in aws_acm_certificate.static_website_certificate.domain_validation_options : d.domain_name => {
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
  zone_id         = aws_route53_zone.oiar.zone_id
}

resource "aws_acm_certificate_validation" "static_website_certificate_validation" {
  provider = aws.us-east-1

  certificate_arn         = aws_acm_certificate.static_website_certificate.arn
  validation_record_fqdns = [for r in aws_route53_record.static_website_certificate_validation : r.fqdn]
}

# ============
# Cloudfront Distribution
# ============

locals {
  # define origin depending on oiar_website_is_active
  oiar_website_active_origin_id = local.oiar_website_is_active ? aws_s3_bucket.oiar_website_buckets["active"].id : aws_s3_bucket.oiar_website_buckets["inactive"].id
  oiar_website_active_terms_and_conditions_viewer_request = local.oiar_website_is_active ? [1] : []
  oiar_website_active_finale_page_viewer_request = local.oiar_website_is_active ? [1] : []
}

resource "aws_cloudfront_origin_access_control" "static_website" {
  name                              = "oiar-website"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "static_website" {
  enabled             = true

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.static_website_access_logs.bucket_domain_name
    prefix          = "cloudfront"
  }

  aliases             = [
    local.domain_names.oiar,
    "www.${local.domain_names.oiar}"
  ]

  default_root_object = "index.html"

  # "active" website
  origin {
    origin_id                = aws_s3_bucket.oiar_website_buckets["active"].id
    domain_name              = aws_s3_bucket.oiar_website_buckets["active"].bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.static_website.id
  }

  # "inactive" website
  origin {
    origin_id                = aws_s3_bucket.oiar_website_buckets["inactive"].id
    domain_name              = aws_s3_bucket.oiar_website_buckets["inactive"].bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.static_website.id
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
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"

    dynamic "lambda_function_association" {
      for_each = local.oiar_website_active_terms_and_conditions_viewer_request
      content {
        event_type   = "viewer-request"
        lambda_arn   = aws_lambda_function.terms_and_conditions_request_lambda.qualified_arn
        include_body = false
      }
    }
  }

  ordered_cache_behavior {
    path_pattern             = "/favicon.ico"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/robots.txt"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/assets/email-logo.png"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/assets/1bf9e1ad-1645-4db1-97a4-13245d644fe5.png"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/assets/c5827104-fa7d-41ad-81e5-f09e150347d8.png"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }


    ordered_cache_behavior {
    path_pattern             = "/94c3/8aa7821f-d685-4318-98a7-a0ef86cd3c49/7fdb23ed-507e-47d5-8d66-00c01ce83915/trailer.mp4"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy_mp4
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/94c3/8aa7821f-d685-4318-98a7-a0ef86cd3c49/script.js"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

    ordered_cache_behavior {
    path_pattern             = "/94c3/8aa7821f-d685-4318-98a7-a0ef86cd3c49/styles.css"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern             = "/94c3/8aa7821f-d685-4318-98a7-a0ef86cd3c49/*"
    allowed_methods          = ["GET", "HEAD", "OPTIONS"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    target_origin_id         = local.oiar_website_active_origin_id
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"

    dynamic "lambda_function_association" {
      for_each = local.oiar_website_active_finale_page_viewer_request
      content {
        event_type   = "viewer-request"
        lambda_arn   = aws_lambda_function.final_page_lambda.qualified_arn
        include_body = false
      }
    }
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



  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.static_website_certificate.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2018"
  }

  price_class = "PriceClass_100" # us and europe
}


resource "aws_route53_record" "static_website" {
  name    = local.domain_names.oiar
  zone_id = aws_route53_zone.oiar.zone_id
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.static_website.domain_name
    zone_id                = aws_cloudfront_distribution.static_website.hosted_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "static_website_www" {
  name    = "www.${local.domain_names.oiar}"
  zone_id = aws_route53_zone.oiar.zone_id
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.static_website.domain_name
    zone_id                = aws_cloudfront_distribution.static_website.hosted_zone_id
    evaluate_target_health = true
  }
}

