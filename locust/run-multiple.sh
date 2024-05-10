#!/bin/bash
export ENDPOINT_NAME=$1
if  [ -z "$ENDPOINT_NAME" ]; then
    echo "Endpoint name not provided"
    echo "Usage ./run-multiple.sh <<endpoint-name>> <<config.sh>> <<users>>"
    exit 1
fi
source "$2"
users=$3
## Iterate over users which is a comma separated list of numbers
for user in ${users//,/ }
do
    echo "Running $user"
    export USERS=$user
    export WORKERS=$user
    export RUN_TIME=5m
    ./distributed.sh $ENDPOINT_NAME "$2" "$user-llama3" ; sleep 6m ;
done




#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-1u.sh 1user-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-5u.sh 5user-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-10u.sh 10u-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-15u.sh 15u-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-20u.sh 20u-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-25u.sh 25-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-30u.sh 30-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-35u.sh 35-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-40u.sh 40-llama3-8b ; sleep 6m ;./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-45u.sh 45-llama3-8b ; sleep 6m ;
#./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 config-tgi-50u.sh 50-llama3-8b ; sleep 6m ;