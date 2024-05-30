## Setup

To get started have an EC2 instance up and running. 

`locust` folder contains `distributed.sh` which kicks off the [distributed locust](https://docs.locust.io/en/stable/running-distributed.html) load test for user and runtime configuration specified in the config files passed to the script . 
```shell
./distributed.sh <<endpoint-name>> [config.sh] [use case label]
./distributed.sh $ENDPOINT_NAME <config.sh> "use_case_label" ;
```
`locust` folder also contains a wrapper file `run-multiple-distributed.sh` which runs for multiple users config specified in the argument. 
```shell
./run-multiple.sh <<endpoint-name>> <<config.sh>> <<users>> <<run-time-minutes>> <usecase-label>
./run-multiple-distributed.sh http://localhost:8080 multi-run-config-bedrock.sh 1,2 1 testing
```
## Load Test

Steps to run a load test:

1. Activate Python environment, and `pip install -r requirements.txt`.
2. Update `locust/bedrock/single-run-config-bedrock.sh` ENV variables, to increase traffic tune users and workers parameters (define users as a multiple of workers): 
   ```
      export RUN_TIME=2m
      export REGION=us-east-1
      export USERS=1
      export WORKERS=1
      export LOCUST_UI=false
      export MAX_NEW_TOKENS=100
      export SCRIPT=locust_script_bedrock_streaming.py
      export PAYLOAD_FILE=chat-1000-tokens.txt
      export USE_CASE=test
   ```
3. Run following commands. 
```shell
cd locust
chmod +x distributed.sh
```
4. Run `./distributed.sh endpoint-name bedrock/single-run-config-bedrock.sh run-lable`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

