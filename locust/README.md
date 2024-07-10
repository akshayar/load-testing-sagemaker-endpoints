## Setup
1. Activate Python environment, and `pip install -r requirements.txt`.
```shell
## Go to source root and run
pip install -r requirements.txt
```
## Test your locust scripts
```shell
cd locust
chmod +x *.sh
./test-py-script.sh <python-script-relative-path> <URL/ModelId> <test-prompt-file-path>
```
#### For LLM deployed using TGI. 
1. Test streaming invocation to measure  first and last token latency
```shell
./test-py-script.sh llm-tgi/locust_script_tgi_streaming.py <URL> <test-prompts>
## Sample
./test-py-script.sh llm-tgi/locust_script_tgi_streaming.py http://ip-172-31-23-118.ec2.internal:8080 ../test-data/chat-1000-tokens.txt
```
2. Test invocation to measure end to end latency
```shell
./test-py-script.sh llm-tgi/locust_script_tgi.py <URL> <test-prompts>
## Sample
./test-py-script.sh llm-tgi/locust_script_tgi.py http://ip-172-31-23-118.ec2.internal:8080 ../test-data/chat-1000-tokens.txt
```
#### For Bedrock testing
1. Test streaming invocation to measure  first and last token latency
```shell
./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py <MODEL_ID> <test-prompts>
## Sample
./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py meta.llama3-8b-instruct-v1:0 ../test-data/chat-1000-tokens.txt
```
2. Test invocation to measure end to end latency
```shell
./test-py-script.sh ./bedrock/locust_script_bedrock.py <MODEL_ID> <test-prompts>
## Sample
./test-py-script.sh ./bedrock/locust_script_bedrock.py meta.llama3-8b-instruct-v1:0 ../test-data/chat-1000-tokens.txt
```
## Run a single load test for N number of users
1. Update environment variables in config file. For example refer [TGI Single Run config](llm-tgi/single-run-config.sh)
. Here are the example config - 
```shell
export RUN_TIME=2m
export REGION=us-east-1
export USERS=1
export WORKERS=1
export LOCUST_UI=false
export MAX_NEW_TOKENS=100
export PAYLOAD_FILE=../test-data/chat-1000-tokens.txt
export USE_CASE=test
```
2. Run following -
```shell
cd locust
chmod +x *.sh
./distributed.sh <URL/ModelId> <single-run-config-path> <python-script-relative-path> <run-lable>
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
4. View logs to monitor progress. 
```shell
tail -f <log-file-printed above>
##Example 
tail -f logs/test/test_30052024175522.log
```
5. Once the run completes view result files at <RESULT_FILE> prefix.  
```shell
ls -ltr <RESULT_FILE>*
##Example 
ls -ltr results/test/test_30052024175522*
```
#### For LLM deployed using TGI.
1. Test streaming invocation to measure  first and last token latency
```shell
## Sample
./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/single-run-config.sh ./llm-tgi/locust_script_tgi_streaming.py 50_llama3_8B_tgi_g5xlarge 
```
2. Test invocation to measure end to end latency
```shell
## Sample
./distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/single-run-config.sh ./llm-tgi/locust_script_tgi.py 50_llama3_8B_tgi_g5xlarge 
```
#### For Bedrock testing
1. Test streaming invocation to measure  first and last token latency
```shell
## Sample
./distributed.sh meta.llama3-8b-instruct-v1:0 ./bedrock/single-run-config.sh ./bedrock/locust_script_bedrock_streaming.py llama3_8B_bedrock 
```
2. Test invocation to measure end to end latency
```shell
## Sample
./distributed.sh meta.llama3-8b-instruct-v1:0 ./bedrock/single-run-config.sh ./bedrock/locust_script_bedrock.py llama3_8B_bedrock 
```

## Run multiple load tests with varrying number of users
1. Run following commands. 
```shell
cd locust
chmod +x *.sh
./run-multiple-distributed.sh <URL/ModelId> <single-run-base-config> \
<python-script-relative-path> <comma-separated-number-of-users>  \
<duration-in-minutes>  <run-lable>

## Following example will run for 1, 5, 10 ... users one after other. 
./run-multiple-distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/multi-run-config.sh \
 ./llm-tgi/locust_script_tgi_streaming.py 1,5,10,15,20,30,35,40,45,50  \
 10  llama3_8B_tgi_g5xlarge

## Running with nohup in background
nohup ./run-multiple-distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/multi-run-config.sh \
 ./llm-tgi/locust_script_tgi_streaming.py 1,5,10,15,20,30,35,40,45,50  \
 10  llama3_8B_tgi_g5xlarge &
```
#### For LLM deployed using TGI.
1. Test streaming invocation to measure  first and last token latency
```shell
## Sample
./run-multiple-distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/multi-run-config.sh \
./llm-tgi/locust_script_tgi_streaming.py 1,5,10,15,20,30,35,40,45,50  \
10 tgi_llama3_g5.xlarge
```
2. Test invocation to measure end to end latency
```shell
## Sample
./run-multiple-distributed.sh http://ip-172-31-23-118.ec2.internal:8080 ./llm-tgi/multi-run-config.sh \
./llm-tgi/locust_script_tgi.py 1,5,10,15,20,30,35,40,45,50  \
10 tgi_llama3_g5.xlarge
```
#### For Bedrock testing
1. Test streaming invocation to measure  first and last token latency
```shell
## Sample
./run-multiple-distributed.sh meta.llama3-8b-instruct-v1:0 ./bedrock/multi-run-config.sh \
./bedrock/locust_script_bedrock_streaming.py 1,5  \
1 llama3_bedrock 
```
2. Test invocation to measure end to end latency
```shell
## Sample
./run-multiple-distributed.sh meta.llama3-8b-instruct-v1:0 ./bedrock/multi-run-config.sh \
./bedrock/locust_script_bedrock.py 1,5  \
1 llama3_bedrock  
```
## Sample Commands
### Sample commands to test locust script for Bedrock
```shell
./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py anthropic.claude-3-sonnet-20240229-v1:0 ../test-data/chat-1000-tokens-anthropic.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py anthropic.claude-3-sonnet-20240229-v1:0 ../test-data/chat-1000-tokens-anthropic.txt

./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py anthropic.claude-3-haiku-20240307-v1:0 ../test-data/chat-1000-tokens-anthropic.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py anthropic.claude-3-haiku-20240307-v1:0 ../test-data/chat-1000-tokens-anthropic.txt

./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py mistral.mistral-7b-instruct-v0:2 ../test-data/chat-1000-tokens-mistral.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py mistral.mistral-7b-instruct-v0:2 ../test-data/chat-1000-tokens-mistral.txt

./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py mistral.mixtral-8x7b-instruct-v0:1 ../test-data/chat-1000-tokens-mistral.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py mistral.mixtral-8x7b-instruct-v0:1 ../test-data/chat-1000-tokens-mistral.txt

./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py mistral.mistral-large-2402-v1:0 ../test-data/chat-1000-tokens-mistral.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py mistral.mistral-large-2402-v1:0 ../test-data/chat-1000-tokens-mistral.txt

./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py meta.llama3-8b-instruct-v1:0 ../test-data/llama3-instruct-1000.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py meta.llama3-8b-instruct-v1:0 ../test-data/llama3-instruct-1000.txt

./test-py-script.sh ./bedrock/locust_script_bedrock_streaming.py meta.llama3-70b-instruct-v1:0 ../test-data/llama3-instruct-1000.txt
./test-py-script.sh ./bedrock/locust_script_bedrock.py meta.llama3-70b-instruct-v1:0 ../test-data/llama3-instruct-1000.txt

```

### Sample commands load test Bedrock
```shell
## Update ./bedrock/single-run-config.sh update PAYLOAD_FILE
./distributed.sh anthropic.claude-3-haiku-20240307-v1:0 ./bedrock/single-run-config.sh ./bedrock/locust_script_bedrock_streaming.py  claude_3_haiku_bedrock

./distributed.sh meta.llama3-70b-instruct-v1:0 ./bedrock/single-run-config.sh ./bedrock/locust_script_bedrock_streaming.py llama3_70B_bedrock

./distributed.sh mistral.mistral-7b-instruct-v0:2 ./bedrock/single-run-config.sh ./bedrock/locust_script_bedrock_streaming.py mistral_mistral_7b_instruct_bedrock

```
## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

