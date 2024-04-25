import json
import logging
import os
import time
import random
import io
import json
import time


import boto3
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events
region = os.environ["REGION"]
content_type = os.environ["CONTENT_TYPE"]
payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]

class TokenIterator:
    def __init__(self, stream,request_meta):
        self.byte_iterator = iter(stream)
        self.request_meta = request_meta
        self.buffer = io.BytesIO()
        self.read_pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        logging.info("iterating")
        try:
            while True:
                self.buffer.seek(self.read_pos)
                line = self.buffer.readline()
                if line and line[-1] == ord("\n"):
                    self.read_pos += len(line) + 1
                    full_line = line[:-1].decode("utf-8")
                    line_data = json.loads(full_line.lstrip("data:").rstrip("/n"))
                    return line_data["token"]["text"]
                chunk = next(self.byte_iterator)
                self.buffer.seek(0, io.SEEK_END)
                self.buffer.write(chunk["PayloadPart"]["Bytes"])
                if(len(line) != 0):
                    string=line.decode('utf-8')
                    self.first_token_time=time.perf_counter()
                    self.request_meta["first_token_time"] = (time.perf_counter() - self.request_meta["start_perf_counter"]) * 1000
                    logging.info(line)
                    return line
        except StopIteration:
            self.request_meta["last_token_time"] = (time.perf_counter() - self.request_meta["start_perf_counter"]) * 1000
            logging.info("The iterator is finished.")
            raise StopIteration("done")

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
        request_meta["start_perf_counter"] = start_perf_counter

        try:
            logging.info("Sending request to SageMaker streaming")
            logging.debug(self.payload)
            response = self.sagemaker_client.invoke_endpoint_with_response_stream(
                EndpointName=self.endpoint_name,
                Body=self.payload,
                ContentType=self.content_type,
            )
            for token in TokenIterator(response["Body"]):
                logging.info(token)
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
