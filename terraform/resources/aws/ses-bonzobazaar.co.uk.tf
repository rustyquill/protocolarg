# ============
# ses setup for bonzobazaar.co.uk
# ============

resource "aws_ses_domain_identity" "bonzobaazar" {
  provider = aws.eu-west-1

  domain = local.domain_names.bonzobazaar
}

resource "aws_ses_domain_mail_from" "bonzobaazar" {
  provider = aws.eu-west-1

  domain           = aws_ses_domain_identity.bonzobaazar.domain
  mail_from_domain = "bounce.${aws_ses_domain_identity.bonzobaazar.domain}"
}


resource "aws_route53_record" "bonzobaazar_ses_verification" {
  zone_id = aws_route53_zone.bonzobaazar.id

  name    = "_amazonses.${aws_ses_domain_identity.bonzobaazar.domain}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.bonzobaazar.verification_token]
}

resource "aws_ses_domain_dkim" "bonzobaazar" {
  provider = aws.eu-west-1

  domain   = aws_ses_domain_identity.bonzobaazar.domain
}

resource "aws_route53_record" "bonzobaazar_ses_dkim_record" {
  count   = 3
  zone_id = aws_route53_zone.bonzobaazar.id
  name    = "${aws_ses_domain_dkim.bonzobaazar.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = "600"
  records = ["${aws_ses_domain_dkim.bonzobaazar.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_route53_record" "bonzobaazar_spf_mail_from" {
  zone_id = aws_route53_zone.bonzobaazar.id
  name    = aws_ses_domain_mail_from.bonzobaazar.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "bonzobaazar_spf_domain" {
  zone_id = aws_route53_zone.bonzobaazar.id
  name    = aws_ses_domain_identity.bonzobaazar.domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "bonzobaazar_mail_from_mx" {
  zone_id = aws_route53_zone.bonzobaazar.id
  name    = aws_ses_domain_mail_from.bonzobaazar.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.eu-west-1.amazonses.com"]
}

resource "aws_route53_record" "bonzobaazar_mail_mx" {
  zone_id = aws_route53_zone.bonzobaazar.id
  name    = aws_route53_zone.bonzobaazar.name
  type    = "MX"
  ttl     = "600"
  records = ["10 inbound-smtp.eu-west-1.amazonaws.com."]
}

