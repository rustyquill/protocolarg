
locals {
  domain_names = {
    oiar = "office-of-incident-assessment-and-response.org.uk"
    bonzoland = "bonzo.land"
    bonzobazaar = "bonzobazaar.co.uk"
    magnusprotocolarg = "themagnusprotocolarg.com"
    magnusinstitute = "themagnusinstitute.org"
    freiheitentschluesseln = "freiheitentschluesseln.de"
  }

  # if set to true the cloudwatch log stream is enabled
  # the logs are streamed to cloudwatch which allow rendering of dashboards!
  cloudwatch_log_stream_enabled = {
    oiar = true
    bonzoland = true
    bonzobazaar = true
    magnusprotocolarg = true
    magnusinstitute = true
    freiheitentschluesseln = true
  }

  # cloudfront managed policies
  cloudfront_cache_policy          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" # CachingDisabled
  cloudfront_origin_request_policy = "b689b0a8-53d0-40ab-baf2-68738e2966ac" # AllViewerExceptHostHeader
  cloudfront_cache_policy_mp4      = "658327ea-f89d-4fab-a63d-7e88639e58f6" # CacheOptimnized

  # email addresses listed here will not auto respond
  # the freddie email address is a real inbox for which we may not want auto replies
  # we can still enable auto replies for this email - this will cause an auto respond and an email in freddies inbox
  email_auto_responder_recipients_exlusion = [
    "MAILER-DAEMON@eu-west-1.amazonses.com",
  ]

  ##
  # services live
  ##

  magnusprotocolarg_website_is_active = true
  email_auto_responder_is_active = true
  oiar_website_is_active = true
  bonzo_land_website_is_active = true
  bonzo_land_nightmare_mode_is_active = true
  bonzobazaar_website_is_active = true
  documentleak_download_link_is_active = true

  forum_challange_is_active = true
  code_challenge_is_active = true

  telnet_challenge_is_active = true

  magnusinstitute_website_is_active = true

  # ec2 configuration for forum and code challenge
  # see tech vault for private key!
  ec2_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIERPhSYudpZNXRlYAgj93gTLEzfBAb6WJwSepHNqqI/8"
  ec2_forum_and_code_challenge = {
    size = "t2.micro"
    root_disk_size = 50
    repository_fqdn = "code-urclna.${local.domain_names.oiar}"
  }

  ec2_telnet_code_challenge = {
    size = "t2.micro"
    root_disk_size = 50
    telnet_fqdn = "tnet.${local.domain_names.oiar}"
  }
}
