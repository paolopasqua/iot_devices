#!/bin/bash

#ps ax | grep arduino_serial.py
# cat running
# DIR=$(dirname $0)
# pkill -f "$DIR/arduino_serial.py"

echo $(ps ax | grep arduino_serial_sql.py)

read PID
if (( $PID != -1 )) ; then
    kill $PID
fi