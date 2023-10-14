# ============
# ses setup for themagnusprotocolarg.com
# ============

resource "aws_ses_domain_identity" "themagnusprotocolarg" {
  provider = aws.eu-west-1

  domain = local.domain_names.magnusprotocolarg
}

resource "aws_ses_domain_mail_from" "themagnusprotocolarg" {
  provider = aws.eu-west-1

  domain           = aws_ses_domain_identity.themagnusprotocolarg.domain
  mail_from_domain = "bounce.${aws_ses_domain_identity.themagnusprotocolarg.domain}"
}


resource "aws_route53_record" "themagnusprotocolarg_ses_verification" {
  zone_id = aws_route53_zone.magnusprotocolarg.id

  name    = "_amazonses.${aws_ses_domain_identity.themagnusprotocolarg.domain}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.themagnusprotocolarg.verification_token]
}

resource "aws_ses_domain_dkim" "themagnusprotocolarg" {
  provider = aws.eu-west-1

  domain   = aws_ses_domain_identity.themagnusprotocolarg.domain
}

resource "aws_route53_record" "themagnusprotocolarg_ses_dkim_record" {
  count   = 3
  zone_id = aws_route53_zone.magnusprotocolarg.id
  name    = "${aws_ses_domain_dkim.themagnusprotocolarg.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = "600"
  records = ["${aws_ses_domain_dkim.themagnusprotocolarg.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_route53_record" "themagnusprotocolarg_spf_mail_from" {
  zone_id = aws_route53_zone.magnusprotocolarg.id
  name    = aws_ses_domain_mail_from.themagnusprotocolarg.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "themagnusprotocolarg_spf_domain" {
  zone_id = aws_route53_zone.magnusprotocolarg.id
  name    = aws_ses_domain_identity.themagnusprotocolarg.domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "themagnusprotocolarg_mail_from_mx" {
  zone_id = aws_route53_zone.magnusprotocolarg.id
  name    = aws_ses_domain_mail_from.themagnusprotocolarg.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.eu-west-1.amazonses.com"]
}
