#!/bin/bash

ps aux | grep -v grep | grep watch_dog | awk '{print $2}' | xargs -r sudo kill -9