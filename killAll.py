#!/bin/bash

# Kill server.py
pkill -f server.py

# Kill autoUpdateScript.py
pkill -f autoUpdateScript.py

echo "Stopped server.py and autoUpdateScript.py"
