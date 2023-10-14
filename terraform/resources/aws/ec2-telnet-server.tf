#
# create an ec2 instance with dns entry
# for "administrative" telnet access
#
#

# ATTENTION: the system does not allow SSH access from the internet to hide away as many ports
# as possible! To access the server via ssh you need to hop over the forum server which is accessible via
# ssh -J 13.42.175.238 ec2-user@<internal telnet server ip address>
#

# ======================================================================================================================
# cloudwatch log group
# ======================================================================================================================

resource "aws_cloudwatch_log_group" "ec2_telnet_logs" {
  name = "ec2-telnet-logs"
  retention_in_days = 90
}


# ======================================================================================================================
# parameter store
# ======================================================================================================================


resource "aws_ssm_parameter" "ec2_telnet_logs" {
  name  = "/rustyquill-arg/telnet/log-group"
  type  = "String"
  value = aws_cloudwatch_log_group.ec2_telnet_logs.name
}


# ======================================================================================================================
# ec2 instance profile
# ======================================================================================================================

resource "aws_iam_instance_profile" "ec2_telnet" {
    name = "ec2_telnet"
    role = aws_iam_role.ec2_telnet.name
}

data "aws_iam_policy_document" "ec2_telnet_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ec2_telnet" {
  name               = "ec2_telnet"
  assume_role_policy = data.aws_iam_policy_document.ec2_telnet_assume_role.json
}

data "aws_iam_policy_document" "ec2_telnet_access" {
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
        aws_cloudwatch_log_group.ec2_telnet_logs.arn,
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

resource "aws_iam_role_policy" "ec2_telnet_access" {
    name   = "ec2_telnet_access"
    role   = aws_iam_role.ec2_telnet.name
    policy = data.aws_iam_policy_document.ec2_telnet_access.json
}

# ======================================================================================================================
# ec2 instance security group
# ======================================================================================================================

resource "aws_security_group" "ec2_telnet" {
    name        = "ec2_telnet"
    description = "ec2_telnet"
}

resource "aws_vpc_security_group_ingress_rule" "ec2_telnet_ssh" {
    security_group_id = aws_security_group.ec2_telnet.id
    description       = "ssh"
    from_port         = 22
    to_port           = 22
    ip_protocol       = "tcp"
    referenced_security_group_id = aws_security_group.ec2_forum.id
}

resource "aws_vpc_security_group_ingress_rule" "ec2_forum_telnet" {
    count = local.telnet_challenge_is_active ? 1 : 0

    security_group_id = aws_security_group.ec2_telnet.id
    description       = "nntp"
    from_port         = 10023
    to_port           = 10023
    ip_protocol       = "tcp"
    cidr_ipv4         = "0.0.0.0/0"
}


resource "aws_vpc_security_group_egress_rule" "ec2_telnet_egress" {
    security_group_id = aws_security_group.ec2_telnet.id
    description       = "all"
    ip_protocol       = "-1"
    cidr_ipv4         = "0.0.0.0/0"
}

# ======================================================================================================================
# ec2 instance
# ======================================================================================================================


locals {
  #ec2_ami_id_to_use = data.aws_ami.amazon_linux_2.id
  ec2_ami_id_to_use_telnet = "ami-08d1da0038a9b642c"
}
resource "aws_instance" "ec2_telnet" {
    instance_type           = local.ec2_telnet_code_challenge.size

    ami                     = local.ec2_ami_id_to_use_telnet
    key_name                = aws_key_pair.key_pair.key_name
    vpc_security_group_ids  = [aws_security_group.ec2_telnet.id]
    user_data               = templatefile("${path.module}/user-data/telnet/ec2-telnet-challenge.sh", {
        docker_compose_sh   = base64encode(file("${path.module}/user-data/telnet/docker-compose.sh"))
        docker_compose_yaml = base64encode(file("${path.module}/user-data/telnet/docker-compose.yaml"))
    })
    iam_instance_profile   = aws_iam_instance_profile.ec2_telnet.name
    root_block_device {
        volume_size = local.ec2_telnet_code_challenge.root_disk_size
    }

    tags = {
        Name = "telnet"
    }

}

resource "aws_route53_record" "ec2_telnet" {
  name    = local.ec2_telnet_code_challenge.telnet_fqdn
  zone_id = aws_route53_zone.oiar.zone_id
  type    = "A"
  ttl     = 300
  records = [aws_instance.ec2_telnet.public_ip]
}


