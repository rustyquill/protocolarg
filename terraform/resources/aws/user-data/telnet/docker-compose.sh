#!/bin/bash
set -e

#
# wrapper script for docker-compose commands
# gets env variables from parameter store before passing them to docker-compose
#

# get env variables from parameter store
telnet_log_group=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/telnet/log-group --output text --query Parameter.Value)

# pass env variables to docker-compose
export TELNET_LOG_GROUP=$telnet_log_group

# run docker-compose
exec docker-compose "$@"
