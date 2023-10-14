#
# creates an s3 bucket for phone system 
# for the ARG
#

resource "aws_s3_bucket" "phone_log_eu_west_2" {
  provider = aws.eu-west-2

  bucket = "rq-arg-phone-log-eu-west-2"
}

resource "aws_s3_bucket_ownership_controls" "phone_log_eu_west_2" {
  provider = aws.eu-west-2

  bucket = aws_s3_bucket.phone_log_eu_west_2.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "phone_log_eu_west_2" {
    provider = aws.eu-west-2

    depends_on = [aws_s3_bucket_ownership_controls.phone_log_eu_west_2]

    bucket = aws_s3_bucket.phone_log_eu_west_2.id
    acl    = "private"
}


