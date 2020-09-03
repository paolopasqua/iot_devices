#!/bin/bash

DIR=$(dirname $0)
# echo "$DIR/arduino_serial.py"
sudo python3 "$DIR/arduino_serial_sql.py" > "$DIR/running" &
# echo $?