#
# create an ec2 instance to host the web  defectors forum
# and the code challenge
#


# ======================================================================================================================
# ec2 eip
# ======================================================================================================================
resource "aws_eip" "ec2_forum_eip" {
    lifecycle {
        prevent_destroy = true
    }
}

# ======================================================================================================================
# cloudwatch log group
# ======================================================================================================================

resource "aws_cloudwatch_log_group" "ec2_forum_challenge_logs" {
  name = "ec2-forum-challenge-logs"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "ec2_code_challenge_logs" {
  name = "ec2-code-challenge-logs"
  retention_in_days = 90
}


# ======================================================================================================================
# parameter store for forum username and password etc
# ======================================================================================================================

resource "aws_ssm_parameter" "ec2_forum_forum_username" {
  name  = "/rustyquill-arg/forum/username"
  type  = "String"
  value = var.forum_username
}

resource "aws_ssm_parameter" "ec2_forum_forum_password" {
  name  = "/rustyquill-arg/forum/password"
  type  = "SecureString"
  value = var.forum_password
}

resource "aws_ssm_parameter" "ec2_forum_cvs_username" {
  name  = "/rustyquill-arg/cvs/username"
  type  = "String"
  value = var.cvs_username
}

resource "aws_ssm_parameter" "ec2_forum_cvs_password" {
  name  = "/rustyquill-arg/cvs/password"
  type  = "SecureString"
  value = var.cvs_password
}

resource "aws_ssm_parameter" "ec2_forum_challenge_logs" {
  name  = "/rustyquill-arg/forum/log-group"
  type  = "String"
  value = aws_cloudwatch_log_group.ec2_forum_challenge_logs.name
}

resource "aws_ssm_parameter" "ec2_code_challenge_logs" {
  name  = "/rustyquill-arg/cvs/log-group"
  type  = "String"
  value = aws_cloudwatch_log_group.ec2_code_challenge_logs.name
}

# ======================================================================================================================
# ec2 instance profile
# ======================================================================================================================

resource "aws_iam_instance_profile" "ec2_forum" {
    name = "ec2_forum"
    role = aws_iam_role.ec2_forum.name
}

data "aws_iam_policy_document" "ec2_forum_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ec2_forum" {
  name               = "ec2_forum"
  assume_role_policy = data.aws_iam_policy_document.ec2_forum_assume_role.json
}

data "aws_iam_policy_document" "ec2_forum_access" {
    # allow access to ecr
    statement {
      effect = "Allow"

      actions = [
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:DescribeImages",
        "ecr:DescribeImageScanFindings",
        "ecr:DescribeRepositories",
        "ecr:GetAuthorizationToken",
        "ecr:GetDownloadUrlForLayer",
        "ecr:GetLifecyclePolicy",
        "ecr:GetLifecyclePolicyPreview",
        "ecr:GetRepositoryPolicy",
        "ecr:ListImages",
        "ecr:ListTagsForResource",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]

      resources = ["*"]
    }

    # allow write access to log group
    statement {
      effect = "Allow"
      actions = [
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]
      resources = [
        aws_cloudwatch_log_group.ec2_code_challenge_logs.arn,
        aws_cloudwatch_log_group.ec2_forum_challenge_logs.arn,
      ]
    }

    # allow read access to parameter store entries
    statement {
      effect = "Allow"
      actions = [
        "ssm:DescribeParameters",
      ]
      resources = ["*"]
    }
    statement {
      effect = "Allow"
      actions = [
        "ssm:GetParameter",
      ]
      resources = ["arn:aws:ssm:*:*:parameter/rustyquill-arg/*"]
    }

}

resource "aws_iam_role_policy" "ec2_forum_access" {
    name   = "ec2_forum_access"
    role   = aws_iam_role.ec2_forum.name
    policy = data.aws_iam_policy_document.ec2_forum_access.json
}

# ======================================================================================================================
# ec2 instance security group
# ======================================================================================================================

resource "aws_security_group" "ec2_forum" {
    name        = "ec2_forum"
    description = "ec2_forum"
}

resource "aws_vpc_security_group_ingress_rule" "ec2_forum_ssh" {
    security_group_id = aws_security_group.ec2_forum.id
    description       = "ssh"
    from_port         = 22
    to_port           = 22
    ip_protocol       = "tcp"
    cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "ec2_forum_nntp" {
    count = local.forum_challange_is_active ? 1 : 0

    security_group_id = aws_security_group.ec2_forum.id
    description       = "nntp"
    from_port         = 119
    to_port           = 119
    ip_protocol       = "tcp"
    cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "ec2_forum_http_monitor" {
    count = local.forum_challange_is_active ? 1 : 0

    security_group_id = aws_security_group.ec2_forum.id
    description       = "nntp monitor"
    from_port         = 12888
    to_port           = 12888
    ip_protocol       = "tcp"
    cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "ec2_forum_code" {
    count = local.code_challenge_is_active ? 1 : 0

    security_group_id = aws_security_group.ec2_forum.id
    description       = "vcs"
    from_port         = 80
    to_port           = 80
    ip_protocol       = "tcp"
    prefix_list_id    = "pl-93a247fa" # cloud front origins prefixes
}

resource "aws_vpc_security_group_egress_rule" "ec2_forum_egress" {
    security_group_id = aws_security_group.ec2_forum.id
    description       = "all"
    ip_protocol       = "-1"
    cidr_ipv4         = "0.0.0.0/0"
}

# ======================================================================================================================
# ec2 instance
# ======================================================================================================================


locals {
  #ec2_ami_id_to_use = data.aws_ami.amazon_linux_2.id
  ec2_ami_id_to_use = "ami-08d1da0038a9b642c"
}
resource "aws_instance" "ec2_forum" {
    instance_type           = local.ec2_forum_and_code_challenge.size

    ami                     = local.ec2_ami_id_to_use
    key_name                = aws_key_pair.key_pair.key_name
    vpc_security_group_ids  = [aws_security_group.ec2_forum.id]
    user_data               = templatefile("${path.module}/user-data/forum/ec2-forum-and-code-challenge.sh", {
        docker_compose_sh   = base64encode(file("${path.module}/user-data/forum/docker-compose.sh"))
        docker_compose_yaml = base64encode(file("${path.module}/user-data/forum/docker-compose.yaml"))
        forum_monitor       = base64encode(file("${path.module}/user-data/forum/forum-monitor.sh"))
    })
    iam_instance_profile   = aws_iam_instance_profile.ec2_forum.name
    root_block_device {
        volume_size = local.ec2_forum_and_code_challenge.root_disk_size
    }

    tags = {
        Name = "forum"
    }

}

# ======================================================================================================================
# ec2 instance eip association
# ======================================================================================================================

resource "aws_eip_association" "ec2_forum" {
    instance_id   = aws_instance.ec2_forum.id
    allocation_id = aws_eip.ec2_forum_eip.id
}

# ======================================================================================================================
# acm certificate for cloudfront distribution
# ======================================================================================================================


resource "aws_acm_certificate" "ec2_forum_certificate" {
  provider = aws.us-east-1

  domain_name               = local.ec2_forum_and_code_challenge.repository_fqdn
  subject_alternative_names = []
  validation_method         = "DNS"
}


resource "aws_route53_record" "ec2_forum_certificate_validation" {
  provider = aws.us-east-1

  for_each = {
    for d in aws_acm_certificate.ec2_forum_certificate.domain_validation_options : d.domain_name => {
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

resource "aws_acm_certificate_validation" "ec2_forum_certificate_validation" {
  provider = aws.us-east-1

  certificate_arn         = aws_acm_certificate.ec2_forum_certificate.arn
  validation_record_fqdns = [for r in aws_route53_record.ec2_forum_certificate_validation : r.fqdn]
}

# ======================================================================================================================
# ec2 cloudfront for code challenge
# ======================================================================================================================

resource "aws_cloudfront_distribution" "ec2_forum" {
  enabled             = true

  aliases             = [
    local.ec2_forum_and_code_challenge.repository_fqdn
  ]

  # ec2 instance
  origin {
    domain_name = aws_instance.ec2_forum.public_dns
    origin_id   = "ec2_forum"
    custom_origin_config {
      http_port             = 80
      https_port            = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
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
    target_origin_id         = "ec2_forum"
    # can;t use forwarded values with policies set
    #origin_request_policy_id = local.cloudfront_origin_request_policy
    #cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"

    forwarded_values {
      query_string = true
      headers      = ["Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers", "Authorization", "Host", "Referer"]
      cookies {
        forward = "all"
      }
    }

    dynamic "lambda_function_association" {
      for_each = local.code_challenge_is_active ? [1] : []
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
    target_origin_id         = "ec2_forum"
    origin_request_policy_id = local.cloudfront_origin_request_policy
    cache_policy_id          = local.cloudfront_cache_policy
    viewer_protocol_policy   = "redirect-to-https"
  }


  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.ec2_forum_certificate.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2018"
  }

  price_class = "PriceClass_100" # us and europe
}


resource "aws_route53_record" "ec2_forum_code_challenge" {
  name    = local.ec2_forum_and_code_challenge.repository_fqdn
  zone_id = aws_route53_zone.oiar.zone_id
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.ec2_forum.domain_name
    zone_id                = aws_cloudfront_distribution.ec2_forum.hosted_zone_id
    evaluate_target_health = true
  }
}


