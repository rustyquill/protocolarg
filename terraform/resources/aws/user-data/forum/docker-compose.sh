#!/bin/bash
set -e

#
# wrapper script for docker-compose commands
# gets env variables from parameter store before passing them to docker-compose
#

# get env variables from parameter store
forum_username=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/forum/username --output text --query Parameter.Value)
forum_password=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/forum/password --with-decryption --output text --query Parameter.Value)
forum_log_group=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/forum/log-group --output text --query Parameter.Value)
cvs_username=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/cvs/username --output text --query Parameter.Value)
cvs_password=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/cvs/password --with-decryption --output text --query Parameter.Value)
cvs_log_group=$(aws ssm get-parameter --region eu-west-2 --name /rustyquill-arg/cvs/log-group --output text --query Parameter.Value)

# pass env variables to docker-compose
export FORUM_USERNAME=$forum_username
export FORUM_PASSWORD=$forum_password
export FORUM_LOG_GROUP=$forum_log_group
export CVS_USERNAME=$cvs_username
export CVS_PASSWORD=$cvs_password
export CVS_LOG_GROUP=$cvs_log_group

# run docker-compose
exec docker-compose "$@"