import json
import logging
import os
import time
import random
import traceback
import gevent.monkey
gevent.monkey.patch_all()

import boto3
import botocore
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events
region = os.environ["REGION"]
payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]
model_id = os.environ["ENDPOINT_NAME"]
content_type = "application/json"
if "TEMPERATURE" in os.environ:
    temperature = os.environ["TEMPERATURE"]
else:
    temperature = 1.0
sampPayloads = []
with open(payload_file, "r") as f:
    sampPayloads = f.read().splitlines()
class BotoClient:
    def __init__(self, host):
        # Consider removing retry logic to get accurate picture of failure in locust
        config = Config(
            region_name=region, retries={"max_attempts": 0, "mode": "standard"}
        )
        self.bedrock_client = boto3.client("bedrock-runtime", config=config)
        self.model_id = model_id
        self.content_type = content_type
        self.max_new_tokens = int(max_new_tokens)
        self.prompt = random.choice(sampPayloads)
        self.payload = json.dumps({"prompt": self.prompt,
                                   "max_gen_len": self.max_new_tokens,
                                   "temperature": float(temperature)
                                   })
        logging.debug("model_id=%s, content_type=%s, payload=%s",
                     self.model_id, self.content_type, self.payload)

    def send(self):
        request_meta = {
            "request_type": "InvokeEndpoint",
            "name": "Bedrock",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        start_perf_counter = time.perf_counter()
        string_len=1

        try:
            logging.debug("Payload:%s",self.payload)
            response = self.bedrock_client.invoke_model(
                body=self.payload,
                modelId=self.model_id,
                accept=self.content_type,
                contentType=self.content_type,
            )
            response_body = json.loads(response.get('body').read())
            logging.debug("Response Body:%s",response_body)
            generated_string = response_body.get('generation')
            string_len=len(generated_string.split())
            logging.info("Prompt: %s | Generated String:%s",self.prompt,generated_string)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                logging.warn('API call limit exceeded; exiting')
                self.user.environment.reached_end = True
                self.user.environment.runner.quit()
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            request_meta["exception"] = e

        response_time_ms=(time.perf_counter() - start_perf_counter)*1000
        time_per_word=response_time_ms/string_len if string_len != 0 else response_time_ms
        time_per_token=response_time_ms/int(max_new_tokens) if int(max_new_tokens) != 0 else response_time_ms
        request_meta["response_time"] = response_time_ms
        logging.info("response_time_ms=%s,time_per_word=%s, time_per_token=%s, string_len=%s",
                     str(response_time_ms), str(time_per_word), str(time_per_token), str(string_len))
        if string_len <= 1:
            request_meta["response_time"] = None
            request_meta["exception"] = 'Zero length output'
        events.request.fire(**request_meta)



class BotoUser(FastHttpUser):
    abstract = True

    def __init__(self, env):
        self.host="http://localhost:8888"
        super().__init__(env)
        self.client = BotoClient(self.host)


class MyUser(BotoUser):
    @task
    def send_request(self):
        self.client.send()

##Write main program to test BotoClient
if __name__ == "__main__":
    ##Set environment HOST to the endpoint name
    #os.environ["HOST"] = "meta.llama2-13b-chat-v1"
    #os.environ["REGION"] = "us-east-1"
    #os.environ["CONTENT_TYPE"] = "application/json"
    #os.environ["PAYLOAD_FILE"] = "chat.txt"
    #os.environ["MAX_NEW_TOKENS"] = "500"
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting locust script")
    logging.info("MODEL_ID=%s", os.environ["ENDPOINT_NAME"])
    logging.info("REGION=%s", os.environ["REGION"])
    logging.info("CONTENT_TYPE=%s", os.environ["CONTENT_TYPE"])
    logging.info("PAYLOAD_FILE=%s", os.environ["PAYLOAD_FILE"])
    logging.info("MAX_NEW_TOKENS=%s", os.environ["MAX_NEW_TOKENS"])
    client = BotoClient(os.environ["HOST"])
    client.send()

