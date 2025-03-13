#!/bin/bash
export $(cat .env | xargs)

tail -f -n 0 "$(echo $APPEND_LOG)" | while read line; do
    FILE_PATH=$(echo "$line" | awk -F':' '{print $2}')
    DIR=$(dirname $FILE_PATH)

    # send file to target servers
    IFS=',' read -r -a ip_array <<< "$(echo $SERVER_TARGET)"
    for ip in "${ip_array[@]}"; do
        echo "$(date '+%Y-%m-%d %H:%M:%S'): Transfer $FILE_PATH to $ip"
        SSH_SERVER=root@$ip
        # check if file dir exists, if not auto create recursive?
        ssh $SSH_SERVER "[ -d $DIR ] || sudo -u www-data mkdir -p $DIR"
        rsync -av --ignore-existing $FILE_PATH $SSH_SERVER:$FILE_PATH
    done
done