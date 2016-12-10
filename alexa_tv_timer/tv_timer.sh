#!/bin/bash

cmds="KEY_MENU KEY_UP KEY_UP KEY_UP KEY_UP KEY_UP KEY_UP KEY_UP KEY_UP KEY_DOWN KEY_DOWN KEY_OK KEY_RIGHT KEY_MENU"

for cmd in $cmds; do
    echo "$cmd"
    if [[ $cmd == "KEY_UP" ]]; then
        delay=0.1
    else
        delay=0.7
    fi 
    irsend SEND_ONCE roshun_vizio_remote $cmd
    sleep $delay
done
