import json
import logging
import os
import time
import random

import boto3
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events
region = os.environ["REGION"]
content_type = os.environ["CONTENT_TYPE"]
payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]


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
            logging.debug(self.payload)
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                Body=self.payload,
                ContentType=self.content_type,
            )
            response_string=response["Body"].read().decode("utf8")
            generated_string=json.loads(response_string)["generated_text"]
            string_len=len(generated_string.split())
            logging.debug(response_string)
        except Exception as e:
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
