#
# configure ses for arg workmail
# ses for oair was created by using aws workmail automatically
# this includes the verification (https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ses_domain_identity_verification)
# we only imported the domain identity itself
# also SES is setup in ireland was workmail is only available in ireland...

# terraform import aws_ses_domain_identity.oiar office-of-incident-assessment-and-response.org.uk
resource "aws_ses_domain_identity" "oiar" {
  provider = aws.eu-west-1

  domain = local.domain_names.oiar
}

# ============
# setup mail from domain
# ============
resource "aws_ses_domain_mail_from" "oiar" {
  provider = aws.eu-west-1

  domain           = aws_ses_domain_identity.oiar.domain
  mail_from_domain = "bounce.${aws_ses_domain_identity.oiar.domain}"
}
resource "aws_route53_record" "oiar_mail_from_mx" {
  zone_id = aws_route53_zone.oiar.id
  name    = aws_ses_domain_mail_from.oiar.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.eu-west-1.amazonses.com"]
}

resource "aws_route53_record" "oiar_mail_from_mx_spf" {
  zone_id = aws_route53_zone.oiar.id
  name    = aws_ses_domain_mail_from.oiar.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}


# ============
# aws ses email receipts for oiar
# auto created by workmail!
# ============

# terraform import aws_ses_receipt_rule_set.oiar INBOUND_MAIL
resource "aws_ses_receipt_rule_set" "oiar" {
  provider = aws.eu-west-1

  rule_set_name = "INBOUND_MAIL" # name auto created by aws workmail!
}

# terraform import aws_ses_receipt_rule.oiar_workmail INBOUND_MAIL:m-17f2cee0a0fc4a1c9dd4bc1b85048c5d
resource "aws_ses_receipt_rule" "oiar_workmail" {
  provider = aws.eu-west-1

  name = "m-17f2cee0a0fc4a1c9dd4bc1b85048c5d" # name auto created by aws workmail!
  rule_set_name = aws_ses_receipt_rule_set.oiar.rule_set_name

  enabled = true
  # react on any ses registeed domain

  recipients = []
  sns_action {
    position = 1
    topic_arn = aws_sns_topic.oiar_email_receiving_topic.arn
  }

  workmail_action {
    position = 2
    organization_arn = "arn:aws:workmail:eu-west-1:952729211370:organization/m-17f2cee0a0fc4a1c9dd4bc1b85048c5d"
    topic_arn = ""
  }
}
