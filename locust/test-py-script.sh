#!/bin/bash
#export HOST="meta.llama2-13b-chat-v1"
export REGION=us-east-1
export CONTENT_TYPE=application/json
export PAYLOAD_FILE=test.txt
export MAX_NEW_TOKENS=500
export HOST=$2
python3 $1