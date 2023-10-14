#
# create ecr repositories for
# server resources (web defectors forum, code challenge...)
#

resource "aws_ecr_repository" "forum" {
  name                 = "forum"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "code_challenge" {
  name                 = "code-challenge"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}


resource "aws_ecr_repository" "telnet" {
  name                 = "telnet"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}


output "code_challenge_ecr_repository_url" {
  value = aws_ecr_repository.code_challenge.repository_url
}
