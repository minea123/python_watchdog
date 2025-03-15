#!/bin/bash
cd $PWD

sudo ./kill.sh
./pull_missing_file.sh

source .venv/bin/activate && nohup python ./watch_dog.py >> watchdog.log 2 >> watchdog.error.log &