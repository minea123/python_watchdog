#!/bin/bash
cd $PWD

sudo ./kill.sh
./pull_missing_file.sh

nohup ./path_watcher.sh >> sent_history.log 2>&1 &
source .venv/bin/activate && nohup python ./watch_dog.py >> sent_history.log 2>&1 &