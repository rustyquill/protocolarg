#!/bin/bash

#
# user data script to setup the forum and code challenge ec2 instance
#

# install docker, docker-compose and ecr helper
yum update -y
amazon-linux-extras install docker
usermod -a -G docker ec2-user
yum install -y amazon-ecr-credential-helper
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# configure docker daemon
# ensure local filesystem can't overflow
cat <<EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
systemctl enable docker
systemctl restart docker

# confiure ecr helper
mkdir /root/.docker
cat <<EOF > /root/.docker/config.json
{
	"credHelpers": {
		"public.ecr.aws": "ecr-login",
		"952729211370.dkr.ecr.eu-west-2.amazonaws.com": "ecr-login"
	}
}
EOF
mkdir /home/ec2-user/.docker
cp /root/.docker/config.json /home/ec2-user/.docker/config.json
chown -R ec2-user:ec2-user /home/ec2-user/.docker

# setup docker-compose file and wrapper
echo ${docker_compose_sh} | base64 -d > /home/ec2-user/docker-compose.sh
chmod +x /home/ec2-user/docker-compose.sh
echo ${docker_compose_yaml} | base64 -d > /home/ec2-user/docker-compose.yaml

# run docker compose
cd /home/ec2-user
./docker-compose.sh up -d
