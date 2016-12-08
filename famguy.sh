#!/bin/bash

cmds="KEY_OK KEY_UP KEY_OK KEY_F KEY_A KEY_M KEY_I KEY_L KEY_Y KEY_Y KEY_DELETE KEY_RIGHT KEY_OK KEY_OK"

irsend SEND_ONCE roshun_vizio_remote KEY_POWER
sleep 20

irsend SEND_ONCE roshun_vizio_remote netflix
sleep 15


for cmd in $cmds; do
    echo "$cmd"
    irsend SEND_ONCE roshun_vizio_remote $cmd
    sleep 1.3
done
