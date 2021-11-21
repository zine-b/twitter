#!/bin/bash

ports_to_kill=(5001 4040 9009 8080)

for port in "${ports_to_kill[@]}"; do
    lsof -ti :$port | xargs kill -9
    echo "Killed processes on port $port"
done