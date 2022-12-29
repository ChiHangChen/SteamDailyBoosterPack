#!/bin/sh
auth=$1

/usr/bin/screen -S steam -d -m python3 SteamMakeBoosterPack.py $auth
