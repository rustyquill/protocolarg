#
# create an iam user with secret access key for phone system
#

resource "aws_iam_user" "phone" {
  name = "phone"
}

resource "aws_iam_access_key" "phone" {
  user = aws_iam_user.phone.name
}

resource "aws_iam_policy" "phone" {
  policy = data.aws_iam_policy_document.phone.json

}


resource "aws_iam_user_policy_attachment" "phone" {
  user = aws_iam_user.phone.name
  policy_arn = aws_iam_policy.phone.arn
}

# https://aws.amazon.com/blogs/security/writing-iam-policies-how-to-grant-access-to-an-amazon-s3-bucket/
data "aws_iam_policy_document" "phone" {
  statement {
    actions = [
    	"s3:ListBucket"
    ]

    resources = ["arn:aws:s3:::rq-arg-phone-log-eu-west-2"]
  }
  statement {
    actions = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
    ]
    resources = ["arn:aws:s3:::rq-arg-phone-log-eu-west-2/*"]
  }
}


#
# output the secrets to push to the github action
#

output "phone_access_key_id" {
  value = aws_iam_access_key.phone.id
}

output "phone_access_key_secret" {
  value = aws_iam_access_key.phone.secret
  sensitive = true
}




