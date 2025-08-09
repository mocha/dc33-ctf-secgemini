#!/bin/bash

binaries=("step1.py" "step2.hs" "step3.js" "step4.pl" "step5" "step6.exe")

read -p "Enter input for binaries: " user_input

for binary in "${binaries[@]}"; do
    echo "$user_input" | ./$binary >/dev/null 2>&1

    exit_status=$?

    if [ $exit_status -ne 0 ]; then
        echo "Wrong flag :("
        exit 1
    fi
done

echo "Flag is correct!"
