#!/bin/bash

for i in {1..50}
do
    echo "Execution $i/50"
    python3 execution_time_client.py
done
