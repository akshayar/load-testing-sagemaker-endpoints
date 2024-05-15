#!/bin/bash
function print_help {
    echo "Usage ./run-multiple.sh <<endpoint-name>> <<config.sh>> <<users>> <<sleep-duration>> <usecase-label>"
    echo "Example ./run-multiple.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-1u.sh 1,2 1m testing"
}
function default_if_empty() {
    if [ -z "$2" ]; then
      echo "$1"
    else
      echo "$2"
    fi
}
export ENDPOINT_NAME=$1
PROPERTY_FILE=$2
users=$3
sleep_duration=$4
use_case_label=$5
use_case_label=$(default_if_empty "-lb-llama3" "$use_case_label")
## Check if input is empty. If empty print help
if [ -z "$ENDPOINT_NAME" ] || [ -z "$PROPERTY_FILE" ] || [ -z "$users" ]; then
    echo "Missing arguments"
    echo "ENDPOINT_NAME=$ENDPOINT_NAME , PROPERTY_FILE=$PROPERTY_FILE , USERS=$USERS"
    print_help
    exit 1
fi

source "$PROPERTY_FILE"

## Iterate over users which is a comma separated list of numbers
for user in ${users//,/ }
do
    echo "Running $user"
    export USERS=$user
    export WORKERS=$user
    export RUN_TIME=5m
    echo "Executing ./distributed.sh $ENDPOINT_NAME "$2" "$user"_"$use_case_label" "
    ./distributed.sh $ENDPOINT_NAME "$2" "$user"_"$use_case_label" ;
    wait $(pgrep locust)
    sleep 1m ;
done




#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-1u.sh 1user-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-5u.sh 5user-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-10u.sh 10u-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-15u.sh 15u-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-20u.sh 20u-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-25u.sh 25-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-30u.sh 30-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-35u.sh 35-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-40u.sh 40-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-45u.sh 45-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-50u.sh 50-llama3-8b ; sleep 6m ;