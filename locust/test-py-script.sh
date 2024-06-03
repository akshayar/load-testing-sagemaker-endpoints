#!/bin/bash
function print_help() {
    echo "Usage: test-py-script.sh <script_path> <host/endpoint/model> <payload_file>"
    echo "Example: test-py-script.sh ./instruct.py meta.llama2-13b-chat-v1 instruct.txt"
    echo "Example: test-py-script.sh ./instruct.py whisper-hf-real-time-endpoint samples.jfk.wav"
}
function default_if_empty() {
    if [ -z "$2" ]; then
      echo "$1"
    else
      echo "$2"
    fi
}
#export HOST="meta.llama2-13b-chat-v1"
#Check if empty arguments or -h and print help
if [ -z "$1" ] || [ -z "$2" ] || [ "$1" == "-h" ]; then
    print_help
    exit 1
fi
export REGION=us-east-1
export CONTENT_TYPE=application/json
export PAYLOAD_FILE=$(default_if_empty "instruct.txt" "$3")
export MAX_NEW_TOKENS=100
export HOST=$2
export ENDPOINT_NAME=$2
python $1
