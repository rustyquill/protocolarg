#
# create an iam user with secret access key
# which can execute the deployments for the oiar website
# the user is then used by the oiar-website github action
#

resource "aws_iam_user" "static_website" {
  name = "static-website-deployment"
}

resource "aws_iam_access_key" "static_website" {
  user = aws_iam_user.static_website.name
}

resource "aws_iam_policy" "static_website" {
  policy = data.aws_iam_policy_document.static_website.json

}

resource "aws_iam_policy" "ecr_repository" {
  policy = data.aws_iam_policy_document.ecr_repository.json
}

resource "aws_iam_user_policy_attachment" "static_website" {
  user = aws_iam_user.static_website.name
  policy_arn = aws_iam_policy.static_website.arn
}

resource "aws_iam_user_policy_attachment" "ecr_repository" {
  user = aws_iam_user.static_website.name
  policy_arn = aws_iam_policy.ecr_repository .arn
}


locals {
  bucket_arns = concat(
    [ for b in aws_s3_bucket.oiar_website_buckets : b.arn ],
    [ for b in aws_s3_bucket.bonzo_website_buckets : b.arn ],
    [ for b in aws_s3_bucket.magnusprotocolarg_website_buckets : b.arn ],
    [ for b in aws_s3_bucket.bonzobazaar_website_buckets : b.arn ],
    [ for b in aws_s3_bucket.themagnusinstitute_website_buckets : b.arn ],
    [ for b in aws_s3_bucket.documentleak_website_buckets : b.arn ],
    [ aws_s3_bucket.lambda_package_us_east_1.arn, aws_s3_bucket.lambda_package_eu_west_1.arn, aws_s3_bucket.lambda_package_eu_west_2.arn ],
    [ aws_s3_bucket.easter_egg_bucket.arn],
  )

  bucket_resources = concat(
    [ for b in aws_s3_bucket.oiar_website_buckets :"${b.arn}/*"],
    [ for b in aws_s3_bucket.bonzo_website_buckets :"${b.arn}/*"],
    [ for b in aws_s3_bucket.magnusprotocolarg_website_buckets :"${b.arn}/*"],
    [ for b in aws_s3_bucket.bonzobazaar_website_buckets :"${b.arn}/*"],
    [ for b in aws_s3_bucket.themagnusinstitute_website_buckets :"${b.arn}/*"],
    [ for b in aws_s3_bucket.documentleak_website_buckets :"${b.arn}/*"],
    [ "${aws_s3_bucket.lambda_package_us_east_1.arn}/*", "${aws_s3_bucket.lambda_package_eu_west_1.arn}/*", "${aws_s3_bucket.lambda_package_eu_west_2.arn}/*" ],
    [ "${aws_s3_bucket.easter_egg_bucket.arn}/*"],
  )

  ecr_repositories = [
    aws_ecr_repository.forum.arn,
    aws_ecr_repository.code_challenge.arn,
    aws_ecr_repository.telnet.arn,
  ]
}

data "aws_iam_policy_document" "static_website" {
  statement {
    actions = [
      "s3:ListBucket",
    ]

    resources = local.bucket_arns
  }
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject"
    ]

    resources = local.bucket_resources
  }
}

data "aws_iam_policy_document" "ecr_repository" {
  statement {
    actions = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    actions = [
      "ecr:ListImages",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetRepositoryPolicy",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
      "ecr:DescribeImages",
      "ecr:BatchGetImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage"
    ]
    resources = local.ecr_repositories
  }
}

#
# output the secrets to push to the github action
#

output "static_website_deployment_access_key_id" {
  value = aws_iam_access_key.static_website.id
}

output "static_website_deployment_access_key_secret" {
  value = aws_iam_access_key.static_website.secret
  sensitive = true
}


