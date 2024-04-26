import json
import logging
import os
import time
import random
import io
import json
import time
import sys


import boto3
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events
region = os.environ["REGION"]
content_type = os.environ["CONTENT_TYPE"]
payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]

# Set root logging
logging.getLogger().setLevel('INFO')

# Add stdout to locust logging
logger = logging.getLogger('locust')
logger.addHandler(logging.StreamHandler(sys.stdout))

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
        with open(payload_file, "r") as f:
            self.sampPayloads = f.read().splitlines()
        self.payload = json.dumps({"inputs": random.choice(self.sampPayloads), "parameters": {"max_new_tokens": self.max_new_tokens}})

    def get_next_string(self,iterator):
        try:
            return next(iterator)["PayloadPart"]["Bytes"].decode('utf-8').strip()
        except StopIteration:
            print("done")
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

        try:
            logging.debug(self.payload)
            response = self.sagemaker_client.invoke_endpoint_with_response_stream(
                EndpointName=self.endpoint_name,
                Body=self.payload,
                ContentType=self.content_type,
            )
            iterator = iter(response["Body"])
            chunk = self.get_next_string(iterator)
            while True:
                chunk = self.get_next_string(iterator)
                if len(chunk) !=0:
                    logging.info(chunk)
                    break

        except Exception as e:
            request_meta["exception"] = e

        request_meta["response_time"] = (
            time.perf_counter() - start_perf_counter
        ) * 1000

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
