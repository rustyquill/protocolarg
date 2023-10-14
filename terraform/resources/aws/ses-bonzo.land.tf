# ============
# ses setup for bonzo.land
# ============

resource "aws_ses_domain_identity" "bonzoland" {
  provider = aws.eu-west-1

  domain = local.domain_names.bonzoland
}

resource "aws_ses_domain_mail_from" "bonzoland" {
  provider = aws.eu-west-1

  domain           = aws_ses_domain_identity.bonzoland.domain
  mail_from_domain = "bounce.${aws_ses_domain_identity.bonzoland.domain}"
}


resource "aws_route53_record" "bonzoland_ses_verification" {
  zone_id = aws_route53_zone.bonzoland.id

  name    = "_amazonses.${aws_ses_domain_identity.bonzoland.domain}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.bonzoland.verification_token]
}

resource "aws_ses_domain_dkim" "bonzoland" {
  provider = aws.eu-west-1

  domain   = aws_ses_domain_identity.bonzoland.domain
}

resource "aws_route53_record" "bonzoland_ses_dkim_record" {
  count   = 3
  zone_id = aws_route53_zone.bonzoland.id
  name    = "${aws_ses_domain_dkim.bonzoland.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = "600"
  records = ["${aws_ses_domain_dkim.bonzoland.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_route53_record" "bonzoland_spf_mail_from" {
  zone_id = aws_route53_zone.bonzoland.id
  name    = aws_ses_domain_mail_from.bonzoland.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "bonzoland_spf_domain" {
  zone_id = aws_route53_zone.bonzoland.id
  name    = aws_ses_domain_identity.bonzoland.domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "bonzoland_mail_from_mx" {
  zone_id = aws_route53_zone.bonzoland.id
  name    = aws_ses_domain_mail_from.bonzoland.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.eu-west-1.amazonses.com"]
}

resource "aws_route53_record" "bonzoland_mail_mx" {
  zone_id = aws_route53_zone.bonzoland.id
  name    = aws_route53_zone.bonzoland.name
  type    = "MX"
  ttl     = "600"
  records = ["10 inbound-smtp.eu-west-1.amazonaws.com."]
}

