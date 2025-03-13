#!/bin/bash
export $(cat .env | xargs)

CONTROL_DIR="/tmp/ssh_mux"

mkdir -p "$CONTROL_DIR"
chmod 700 "$CONTROL_DIR"

cleanup() {
    echo "Cleaning up SSH connections..."
    for ip in "${ip_array[@]}"; do
        SSH_SERVER="root@$ip"
        CONTROL_PATH="$CONTROL_DIR/ssh_mux_${SSH_SERVER//:/_}"
        ssh -S "$CONTROL_PATH" -O exit "$SSH_SERVER" 2>/dev/null
    done
}
trap cleanup EXIT

stdbuf -oL tail -f -n 0 "$(echo $APPEND_LOG)" | while read line; do
    FILE_PATH=$(echo "$line" | awk -F':' '{print $2}')
    DIR=$(dirname $FILE_PATH)

    # send file to target servers
    IFS=',' read -r -a ip_array <<< "$(echo $SERVER_TARGET)"
    for ip in "${ip_array[@]}"; do
        echo "$(date '+%Y-%m-%d %H:%M:%S'): Transfer $FILE_PATH to $ip"
        SSH_SERVER=root@$ip
        CONTROL_PATH="$CONTROL_DIR/ssh_mux_${SSH_SERVER//:/_}"

        if [ ! -S "$CONTROL_PATH" ]; then
            echo "Starting persistent SSH connection to $SSH_SERVER..."
            ssh -M -S "$CONTROL_PATH" -o ControlPersist=600 -o ConnectTimeout=10 "$SSH_SERVER" "true" &
            sleep 1  # Give it a moment to establish
        fi

        # check if file dir exists, if not auto create recursive?
        ssh -S "$CONTROL_PATH" $SSH_SERVER "[ -d $DIR ] || sudo -u www-data mkdir -p $DIR"
        rsync -av --ignore-existing --timeout=30 -e "ssh -S $CONTROL_PATH" $FILE_PATH $SSH_SERVER:$FILE_PATH
    done
done