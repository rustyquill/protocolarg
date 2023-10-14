#
# create the ssh keypair used for ssh access
# see the tech vault for the private key!
#

resource "aws_key_pair" "key_pair" {
  key_name   = "linux-key-pair"  
  public_key = local.ec2_public_key
}
