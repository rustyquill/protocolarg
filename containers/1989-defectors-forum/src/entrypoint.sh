#!/bin/sh
set -e

[ -z "${GROUP_USERNAME}" ] && echo "no group username for membership only access sepcified. defaulting to 'username'" && export GROUP_USERNAME=username
[ -z "${GROUP_PASSWORD}" ] && echo "no group password for membership only access sepcified. defaulting to 'password'" && export GROUP_PASSWORD=password
envsubst '${GROUP_USERNAME} ${GROUP_PASSWORD}' < /etc/news/nnrp.access.template > /etc/news/nnrp.access

# start rsyslogd
tail --pid $$ -F /var/log/syslog &
/usr/sbin/rsyslogd
# quick n dirty sleep so the log files in syslog are in order
sleep 1

# handover entrypoint to news server
exec "$@"
