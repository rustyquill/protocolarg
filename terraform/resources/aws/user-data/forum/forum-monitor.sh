#!/bin/sh

#
# This script is used to monitor the forum application
# by testing the port being open with netcat.
#

FILE="${1}"
[ -z "${FILE}" ] && echo "please provide a file to monitor" && exit 1

while true; do
    sleep 60
    nc -zv localhost 119
    forum_accessible_status="failed"
    if [ $? -eq 0 ]; then
        forum_accessible_status="ok"
    fi

    # create ohdear json check result
    cat << EOF > "${FILE}"
{
    "finishedAt": "$(date +%s)",
    "checkResults": [
        {
            "name": "forum accessible",
            "status": "${forum_accessible_status}",
            "label": "forum accessible",
            "notificationMessage": "forum accessible",
            "shortSummary": "119",
            "meta": {}
        }
    ]

}
EOF
done
