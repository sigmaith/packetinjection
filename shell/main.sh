#!/bin/bash

while true; do
    # 프로토콜 입력 루프
    while true; do
        echo "Enter testing protocol (or 'exit' to quit):"
        read protocol
        echo -e "\n"
        if [[ "$protocol" == "exit" ]]; then
            echo "Exiting."
            exit 0
        fi

        protocol_path="./$protocol"
        if [[ -d "$protocol_path" ]]; then
            break
        else
            echo "The protocol does not exist, please enter proper protocol."
            echo -e "\n"
        fi
    done

    cd "$protocol_path"

    # rule 입력 루프
    while true; do
        echo "Enter testing rule file for the selected protocol (or 'exit' to quit):"
        echo "<Rule lists>"
        ls -1
        read rule
        echo -e "\n"
        if [[ "$rule" == "exit" ]]; then
            echo "Exiting."
            exit 0
        fi

        rule_path="./$rule"
        if [[ -d "$rule_path" ]]; then
            break
        else
            echo "The rule does not exist, please enter proper rule file."
            echo -e "\n"
        fi
    done

    # 폴더로 이동
    cd "$rule_path"

    # scenario 입력 루프
    while true; do
        echo "Enter Scenario (or 'exit' to quit):"
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
            awk -F" : " '/# Description/{print $3}' "$scenario_file" | tr -d '\r'

            if [[ -n "$python_script" ]]; then
                # 절대 경로로 확인
                script_path=$(readlink -f "$python_script")
                #echo "Absolute path of the Python script: $script_path"

                if [[ -f "$script_path" ]]; then
                    #echo "Python script exists: $script_path"
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
            echo "The scenario does not exist, please enter proper scenario."
            echo -e "\n"
        fi
    done

    # 캡처 파일 이름, 경로 설정 
    capture_filename="$(basename "${scenario_file%.txt}")_$(date +%Y%m%d%H%M%S).pcap"
    OUTPUT_FILE="/mnt/c/Users/admin/Documents/jiyun/shell/modbus/result/${capture_filename}"

    # tcpdump 캡처 시작
    sudo tcpdump -i eth0 -w "$OUTPUT_FILE" &
    TCPDUMP_PID=$!

    start_time=$(date +%s)
    python3 "$script_path" "$scenario_file"
    end_time=$(date +%s)

    # tcpdump 캡처 종료
    sudo kill $TCPDUMP_PID

    result=$?

    # 요약 정보 출력
    execution_time=$((end_time - start_time))
    echo -e "\n"
    echo "<Summary>"
    echo "Selected protocol: $protocol"
    echo "Execution time: ${execution_time} seconds"
    if [ $result -eq 0 ]; then
        echo "Testing result: success"
    else
        echo "Testing result: fail"
    fi

    # 원래 디렉토리로 돌아가기
    cd /mnt/c/Users/admin/Documents/jiyun/shell
    echo -e "\n"
    # 사용자에게 반복할 것인지 묻기
    echo "Do you want to run another test? (y/n):"
    read answer
    if [[ "$answer" != "y" ]]; then
        break
    fi
done
