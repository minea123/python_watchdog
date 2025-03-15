#!/bin/bash

export $(cat .env | xargs)

echo "start initial syncronize..."

IFS=',' read -r -a ip_array <<< "$(echo $SERVER_TARGET)"
for ip in "${ip_array[@]}"; do
    ip=$(echo "$ip" | sed 's/http:\/\///' | sed 's/:.*//')
    echo "Start initial sync from server $ip"
    SSH_SERVER=root@$ip
    rsync -avz --progress --ignore-existing --exclude 'mpdf' $SSH_SERVER:/App/aii_school_prod/storage/app /App/aii_school_prod/storage
done

sudo chown www-data:www-data  -R /App/aii_school_prod/storage
sudo chown 755 -R /App/aii_school_prod/storage