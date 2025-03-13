#!/bin/bash

ps aux | grep -v grep | grep watch_dog | awk '{print $2}' | xargs -r sudo kill -9
ps aux | grep -v grep | grep "tail -f -n 0" | awk '{print $2}' | xargs -r sudo kill -9