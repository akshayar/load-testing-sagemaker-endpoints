import json
import logging
import os
import time
import random
import io
import json
import time
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

        try:
            logging.debug("Payload:%s",self.payload)
            response = self.sagemaker_client.invoke_endpoint_with_response_stream(
                EndpointName=self.endpoint_name,
                Body=self.payload,
                ContentType=self.content_type,
            )
            self.get_first_string(response)
            response_time_ms=(time.perf_counter() - start_perf_counter)*1000
            request_meta["response_time"] = response_time_ms
            logging.info("response_time_ms=%s", str(response_time_ms))
            events.request.fire(**request_meta)
            self.drain_stream(response)
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            request_meta["exception"] = e

    def get_next_string(self,iterator):
        return next(iterator)["PayloadPart"]["Bytes"].decode('utf-8').strip()

    def get_first_string(self,response):
        try:
            iterator = iter(response["Body"])
            chunk = self.get_next_string(iterator)
            i=0
            while True:
                chunk = self.get_next_string(iterator)
                logging.debug("Iterating response no %s : %s",str(i),chunk)
                if chunk and chunk != '\n' and len(chunk) !=0:
                    logging.info("First token: %s",chunk)
                    return chunk
                i+=1
        except StopIteration:
            print("done")

    def drain_stream(self,response):
        logging.info("Draining response stream")
        iterator = iter(response["Body"])
        try:
            chunk = self.get_next_string(iterator)
            i=0
            while True:
                chunk = self.get_next_string(iterator)
                i+=1
        except StopIteration:
            logging.info("done")
            return


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
    #os.environ["PAYLOAD_FILE"] = "test.txt"
    #os.environ["MAX_NEW_TOKENS"] = "500"
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting locust script")
    logging.info("HOST=%s", os.environ["HOST"])
    logging.info("REGION=%s", os.environ["REGION"])
    logging.info("CONTENT_TYPE=%s", os.environ["CONTENT_TYPE"])
    logging.info("PAYLOAD_FILE=%s", os.environ["PAYLOAD_FILE"])
    logging.info("MAX_NEW_TOKENS=%s", os.environ["MAX_NEW_TOKENS"])
    client = BotoClient(os.environ["HOST"])
    client.send()