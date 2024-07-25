#!/bin/bash

while true; do
    echo "Enter testing protocol directory name (or 'exit' to quit):"
    read protocol_dir
    echo -e "\n"
    if [[ "$protocol_dir" == "exit" ]]; then
        echo "Exiting."
        exit 0
    fi

    protocol_path="/home/seslab/seslab/shell/$protocol_dir"
    if [[ -d "$protocol_path" ]]; then
        break
    else
        echo "The protocol directory does not exist, please enter a valid directory."
        echo -e "\n"
    fi
done

cd "$protocol_path"

while true; do
    echo "Enter testing rule directory name for the selected protocol (or 'exit' to quit):"
    echo "<Rule lists>"
    ls -1
    read rule_dir
    echo -e "\n"
    if [[ "$rule_dir" == "exit" ]]; then
        echo "Exiting."
        exit 0
    fi

    rule_path="$protocol_path/$rule_dir"
    if [[ -d "$rule_path" ]]; then
        break
    else
        echo "The rule directory does not exist, please enter a valid directory."
        echo -e "\n"
    fi
done

cd "$rule_path"

while true; do
    echo "Enter scenario file name (without .txt) (or 'exit' to quit):"
    echo "<Scenario lists>"
    ls -1 | grep "\.txt$" | sed 's/\.txt$//'
    read scen
    echo -e "\n"
    if [[ "$scen" == "exit" ]]; then
        echo "Exiting."
        exit 0
    fi

    scenario_file="${scen}.txt"
    if [[ -f "$scenario_file" ]]; then
        python_script=$(awk '/^# PythonScript: /{print $3}' "$scenario_file" | tr -d '\r')
        echo "Scenario file: $scenario_file"
        echo "Python script: $python_script"
        echo "Description:"
        awk '/# Description/{print substr($0, index($0,$3))}' "$scenario_file" | tr -d '\r'

        if [[ -n "$python_script" ]]; then
            script_path="$rule_path/$python_script"

            if [[ -f "$script_path" ]]; then
                break
            else
                echo "The Python script for the selected scenario does not exist at $script_path."
                echo "Checking if the file exists manually:"
                ls -l "$script_path"
                echo -e "\n"
            fi
        else
            echo "The Python script for the selected scenario does not exist."
            echo -e "\n"
        fi
    else
        echo "The scenario file does not exist, please enter a valid scenario file."
        echo -e "\n"
    fi
done

capture_filename="$(basename "${scenario_file%.txt}")_$(date +%Y%m%d%H%M%S).pcap"
OUTPUT_FILE="$protocol_path/result/${capture_filename}"

echo "Starting tcpdump on enp86s0..."
sudo tcpdump -i enp86s0 -w "$OUTPUT_FILE" &
TCPDUMP_PID=$!
sleep 2

start_time=$(date +%s)
python3 "$script_path" "$scenario_file"
end_time=$(date +%s)

if ps -p $TCPDUMP_PID > /dev/null
then
   echo "Stopping tcpdump..."
   sudo kill $TCPDUMP_PID
fi

result=$?

sudo chown seslab:seslab "$OUTPUT_FILE"

execution_time=$((end_time - start_time))
echo -e "\n"
echo "<Summary>"
echo "Selected protocol: $protocol_dir"
echo "Execution time: ${execution_time} seconds"
if [ $result -eq 0 ]; then
    echo "Testing result: success"
else
    echo "Testing result: fail"
fi

cd /home/seslab/seslab/shell
echo -e "\n"
echo "Do you want to run another test? (y/n):"
read answer
if [[ "$answer" != "y" ]]; then
    break
fi
done
