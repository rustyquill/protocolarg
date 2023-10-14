#
# create the dns zone for oiar
#

# ============
# route53 zones
# ============

resource "aws_route53_zone" "oiar" {
  name = local.domain_names.oiar
}

resource "aws_route53_zone" "bonzoland" {
  name = local.domain_names.bonzoland
}

resource "aws_route53_zone" "bonzobaazar" {
  name = local.domain_names.bonzobazaar
}

resource "aws_route53_zone" "magnusprotocolarg" {
  name = local.domain_names.magnusprotocolarg
}

resource "aws_route53_zone" "magnusinstitute" {
  name = local.domain_names.magnusinstitute
}

resource "aws_route53_zone" "freiheitentschluesseln" {
  name = local.domain_names.freiheitentschluesseln
}

# ============
# route53 entries for aws workmail
# workmail automatically creates these entries
# ============

# terraform import aws_route53_record.amazon_workmail_mx Z087221039IJPC76GY1H4_office-of-incident-assessment-and-response.org.uk_MX
resource "aws_route53_record" "amazon_workmail_mx" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = local.domain_names.oiar
  type    = "MX"
  ttl     = 600
  records = [
    "10 inbound-smtp.eu-west-1.amazonaws.com."
  ]
}

# terraform import aws_route53_record.amazon_ses_txt Z087221039IJPC76GY1H4__amazonses.office-of-incident-assessment-and-response.org.uk_TXT
resource "aws_route53_record" "amazon_ses_txt" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = "_amazonses.${local.domain_names.oiar}"
  type    = "TXT"
  ttl     = 600
  records = [
    "Pb35lB/2/KyY9LO2oRhPuqBImSlUztXyDYE5CoEfQuw="
  ]
}

# terraform import aws_route53_record.amazon_dkim_1 Z087221039IJPC76GY1H4_hsa3afx4a7d4keh4gwxhwx743mwkzwa7._domainkey.office-of-incident-assessment-and-response.org.uk_CNAME
resource "aws_route53_record" "amazon_dkim_1" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = "hsa3afx4a7d4keh4gwxhwx743mwkzwa7._domainkey.${local.domain_names.oiar}"
  type    = "CNAME"
  ttl     = 600
  records = [
    "hsa3afx4a7d4keh4gwxhwx743mwkzwa7.dkim.amazonses.com."
  ]
}

# terraform import aws_route53_record.amazon_dkim_2 Z087221039IJPC76GY1H4_ja25vlhay656af3qsskhmaw6mnrqqgzq._domainkey.office-of-incident-assessment-and-response.org.uk_CNAME
resource "aws_route53_record" "amazon_dkim_2" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = "ja25vlhay656af3qsskhmaw6mnrqqgzq._domainkey.${local.domain_names.oiar}"
  type    = "CNAME"
  ttl     = 600
  records = [
    "ja25vlhay656af3qsskhmaw6mnrqqgzq.dkim.amazonses.com."
  ]
}

# terraform import aws_route53_record.amazon_dkim_3 Z087221039IJPC76GY1H4_qxrws4hygfnitqrapwxjnrosf55pkb66._domainkey.office-of-incident-assessment-and-response.org.uk_CNAME
resource "aws_route53_record" "amazon_dkim_3" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = "qxrws4hygfnitqrapwxjnrosf55pkb66._domainkey.${local.domain_names.oiar}"
  type    = "CNAME"
  ttl     = 600
  records = [
    "qxrws4hygfnitqrapwxjnrosf55pkb66.dkim.amazonses.com."
  ]
}

# terraform import aws_route53_record.amazon_autodiscover Z087221039IJPC76GY1H4_autodiscover.office-of-incident-assessment-and-response.org.uk_CNAME
resource "aws_route53_record" "amazon_autodiscover" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = "autodiscover.${local.domain_names.oiar}"
  type    = "CNAME"
  ttl     = 600
  records = [
    "autodiscover.mail.eu-west-1.awsapps.com."
  ]
}

# ============
# route53 entries for spf and dmarc
# for workmail
# ============

resource "aws_route53_record" "amazon_workmail_spf" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = local.domain_names.oiar
  type    = "TXT"
  ttl     = 600
  records = [
    "v=spf1 include:amazonses.com ~all"
  ]
}

resource "aws_route53_record" "amazon_workmail_dmarc" {
  zone_id = aws_route53_zone.oiar.zone_id
  name    = "_dmarc.${local.domain_names.oiar}"
  type    = "TXT"
  ttl     = 600
  records = [
    "v=DMARC1;p=quarantine;pct=100;fo=1"
  ]
}
