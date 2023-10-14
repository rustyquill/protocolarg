#!/bin/sh
set -e

[ -z "${CVS_USERNAME}" ] && echo "no cvs username for membership only access sepcified. defaulting to 'username'" && export CVS_USERNAME=username
[ -z "${CVS_PASSWORD}" ] && echo "no cvs password for membership only access sepcified. defaulting to 'password'" && export CVS_PASSWORD=password
# loop trough all usernames given (comma separeted) and create a htpasswd entry
# for each of them
for username in $(echo ${CVS_USERNAME} | tr "," "\n"); do
    if [ ! -f /etc/apache2/.htpasswd ]; then
        htpasswd -bc /etc/apache2/.htpasswd ${username} ${CVS_PASSWORD}
    else
        htpasswd -b /etc/apache2/.htpasswd ${username} ${CVS_PASSWORD}
    fi
done

# handover to CMD
exec "$@"
