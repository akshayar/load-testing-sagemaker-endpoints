## Setup
1. Activate Python environment, and `pip install -r requirements.txt`.
## Test Scripts
```shell
cd locust
chmod +x *.sh
./test-py-script.sh llm-tgi/locust_script_tgi_streaming.py <URL> <test-prompts>
## Sample
./test-py-script.sh llm-tgi/locust_script_tgi_streaming.py http://ip-172-31-23-118.ec2.internal:8080 ../test-data/chat-1000-tokens.txt
```
## Run a single load test for N number of users
1. Update `locust/llm-tgi/single-run-config-bedrock.sh` ENV variables, to increase traffic tune users and workers parameters (define users as a multiple of workers):
   ```
      ## Run time in mins
      export RUN_TIME=2m
      export REGION=us-east-1
      export USERS=1
      export WORKERS=1
      export LOCUST_UI=false
      export MAX_NEW_TOKENS=100
      export PAYLOAD_FILE=chat-1000-tokens.txt
      ## Use case label
      export USE_CASE=test
   ```
2. Run following -
```shell
cd locust
chmod +x *.sh
./distributed.sh <URL> <run-config> ./llm-tgi/locust_script_tgi_streaming.py <run-lable>
## Sample
./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/multi-run-config.sh ./llm-tgi/locust_script_tgi_streaming.py 50_llama3_8B_tgi_g5xlarge 
```
3. The output will look like - 
```shell
ENDPOINT_NAME: http://ip-172-31-23-118.ec2.internal:8080
USE_CASE: test
CONTENT_TYPE: application/json
RUN_TIME: 2m
PAYLOAD_FILE: ../test-data/chat-1000-tokens.txt
REGION: us-east-1
USERS: 1
WORKERS: 1
LOCUST_UI: false
MAX_NEW_TOKENS: 100
TIMESTAMP: 30052024175522
LOG_FILE: logs/test/test_30052024175522.log
STD_OUT: logs/test/test_30052024175522.out
RESULT_FILE: results/test/test_30052024175522
HTML_RESULT_FILE: results/test/test_30052024175522.html
SCRIPT: bedrock/locust_script_bedrock_streaming.py

```
## Run multiple load tests with for 1,5,10,10 users

1. Run following commands. 
```shell
cd locust
chmod +x *.sh
./run-multiple-distributed.sh <URL> <multi-run-base-config> \
./llm-tgi/locust_script_tgi_streaming.py <comma-separated-number-of-users>  \
<duration-in-minutes>  <run-lable>


./run-multiple-distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/multi-run-config.sh \
 ./llm-tgi/locust_script_tgi_streaming.py 1,5,10,15,20,30,35,40,45,50  \
 10  llama3_8B_tgi_g5xlarge
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

