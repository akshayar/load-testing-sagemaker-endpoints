import json
import logging
import os
import time
import random
import io
import json
import time
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
        self.bedrock_client = boto3.client("bedrock-runtime", config=config)
        self.model_id = host.split("/")[-1]
        self.content_type = content_type
        self.max_new_tokens = int(max_new_tokens)
        self.prompt = random.choice(sampPayloads)
        self.payload = json.dumps({"prompt": self.prompt,
                                   "max_gen_len": self.max_new_tokens
                                   })
        logging.debug("model_id=%s, content_type=%s, payload=%s",
                     self.model_id, self.content_type, self.payload)

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
            response = self.bedrock_client.invoke_model_with_response_stream(
                body=self.payload,
                modelId=self.model_id,
                accept=self.content_type,
                contentType=self.content_type,
            )
            self.get_first_string(response)
            response_time_ms=(time.perf_counter() - start_perf_counter)*1000
            request_meta["response_time"] = response_time_ms
            logging.info("response_time_ms=%s", str(response_time_ms))
            events.request.fire(**request_meta)
        except Exception as e:
            logging.error(e)
            request_meta["exception"] = e


    def get_first_string(self,response):
        try:
            stream = response.get('body')
            logging.debug("Stream response:%s",stream)
            i = 1
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_obj = json.loads(chunk.get('bytes').decode())
                        logging.debug("Iterating response no %s : %s",str(i),chunk)
                        text = chunk_obj['generation'].strip()
                        if len(text) !=0:
                            logging.info("First token: %s",text)
                            return text
                        i+=1
        except StopIteration:
            print("done")


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