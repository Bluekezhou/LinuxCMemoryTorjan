#!/bin/bash

make 
socat tcp4-listen:4444,fork exec:./company &
python exp.py &
python cmd_server.py
