#!/bin/bash

export $(cat .env | xargs)

echo "start initial syncronize..."

IFS=',' read -r -a ip_array <<< "$(echo $SERVER_TARGET)"
for ip in "${ip_array[@]}"; do
    echo "Start initial sync from server $ip"
    SSH_SERVER=root@$ip
    rsync -avz --progress --ignore-existing --exclude 'mpdf' $SSH_SERVER:/App/aii_school_prod/storage/app /App/aii_school_prod/storage
done