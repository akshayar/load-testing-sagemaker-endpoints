import json
import logging
import os
import time
import random
import traceback
import gevent.monkey
gevent.monkey.patch_all()

import boto3
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events
region = os.environ["REGION"]
content_type = os.environ["CONTENT_TYPE"]
payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]
sampPayloads = []
with open(payload_file, "r") as f:
    sampPayloads = f.read().splitlines()
class BotoClient:
    def __init__(self, host):
        # Consider removing retry logic to get accurate picture of failure in locust
        config = Config(
            region_name=region, retries={"max_attempts": 0, "mode": "standard"}
        )
        self.sagemaker_client = boto3.client("sagemaker-runtime", config=config)
        self.endpoint_name = host.split("/")[-1]
        self.content_type = content_type
        self.max_new_tokens = int(max_new_tokens)
        self.prompt = random.choice(sampPayloads)
        self.payload = json.dumps({"inputs": self.prompt,
                                   "parameters": {"max_new_tokens": self.max_new_tokens}}
                                  )
        # Log the details above
        logging.debug("endpoint_name=%s, content_type=%s, payload=%s",
                     self.endpoint_name, self.content_type, self.payload)

    def send(self):
        request_meta = {
            "request_type": "InvokeEndpoint",
            "name": "SageMaker",
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
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                Body=self.payload,
                ContentType=self.content_type,
            )

            response_string=response["Body"].read().decode("utf8")
            logging.debug("Response Body:%s",response_string)
            generated_string=json.loads(response_string)[0]["generated_text"]
            string_len=len(generated_string.split())
            logging.info("Prompt: %s | Generated String:%s",self.prompt,response_string)
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            request_meta["exception"] = e

        response_time_ms=(time.perf_counter() - start_perf_counter)*1000
        time_per_word=response_time_ms/string_len
        time_per_token=response_time_ms/int(max_new_tokens)
        request_meta["response_time"] = response_time_ms
        logging.info("response_time_ms=%s,time_per_word=%s, time_per_token=%s, string_len=%s",
                     str(response_time_ms), str(time_per_word), str(time_per_token), str(string_len))
        events.request.fire(**request_meta)


class BotoUser(FastHttpUser):
    abstract = True

    def __init__(self, env):
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
    logging.info("HOST=%s", os.environ["HOST"])
    logging.info("REGION=%s", os.environ["REGION"])
    logging.info("CONTENT_TYPE=%s", os.environ["CONTENT_TYPE"])
    logging.info("PAYLOAD_FILE=%s", os.environ["PAYLOAD_FILE"])
    logging.info("MAX_NEW_TOKENS=%s", os.environ["MAX_NEW_TOKENS"])
    client = BotoClient(os.environ["HOST"])
    client.send()