#!/bin/bash

while true; do
    directories=$(ls -d */ | grep -vE '^log/$|^packet history/$' | sed 's#/##')
    echo "Choose protocol: $directories or exit"
    read protocol

    if [[ "$protocol" == "exit" ]]; then
        echo "$(date): Exited NPP_APP" >> /protocol/log/activity.log
        exit 0
    fi

    if [[ -d $protocol ]]; then
        cd $protocol
        echo "$(date): Selected $protocol" >> /protocol/log/activity.log

        scenarios=$(ls *.py | sed 's/\.py//')
        echo "Select a scenario: $scenarios or exit"
        read scen

        if [[ "$scen" == "exit" ]]; then
            cd ..
            continue
        fi

        if [[ -f "$scen.py" ]]; then
            echo "$(date): Running $scen" >> /protocol/log/activity.log
            python $scen.py
        else
            cd ..
        fi
    fi
done