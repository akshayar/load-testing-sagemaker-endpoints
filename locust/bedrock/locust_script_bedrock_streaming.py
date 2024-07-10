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
import botocore
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events
from bedrock_script_common import *


region = os.environ["REGION"]
payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]
model_id = os.environ["ENDPOINT_NAME"]
temperature = get_env_or_default("TEMPERATURE", 1.0)
min_latency = get_env_or_default("MIN_LATENCY", 100)
content_type = "application/json"
get_next_function = find_get_next_function(model_id)


samplePayloads = []
with open(payload_file, "r") as f:
    samplePayloads = f.read().splitlines()


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
        self.prompt = random.choice(samplePayloads)
        self.payload = generate_payload(self.model_id,self.prompt,self.max_new_tokens,temperature)
        self.final_output = []
        logging.debug("model_id=%s, content_type=%s, payload=%s",
                      self.model_id, self.content_type, self.payload)

    def send(self):
        first_token_metadata = {
            "request_type": "FirstToken",
            "name": "Bedrock",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        last_token_metadata = {
            "request_type": "LastToken",
            "name": "Bedrock",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        start_perf_counter = time.perf_counter()

        try:
            logging.info("Payload:%s", self.payload)
            response = self.bedrock_client.invoke_model_with_response_stream(
                body=self.payload,
                modelId=self.model_id,
                accept=self.content_type,
                contentType=self.content_type,
            )
            logging.info("Response:%s", response)
            self.get_first_string(response)
            response_time_ms = (time.perf_counter() - start_perf_counter) * 1000
            self.drain_stream(response)
            response_time_last_token_ms = (time.perf_counter() - start_perf_counter) * 1000
            first_token_metadata["response_time"] = response_time_ms
            last_token_metadata["response_time"] = response_time_last_token_ms
            diff = response_time_last_token_ms - response_time_ms
            if diff <= int(min_latency):
                logging.info("Error response as diff=%s is less than %s", str(diff), str(min_latency))
                raise Exception("Error response as diff=%s is less than %s", str(diff), str(min_latency))
            logging.info("response_time_ms=%s | response_time_last_token_ms=%s", str(response_time_ms),
                         str(response_time_last_token_ms))
        except botocore.exceptions.ClientError as error:
            traceback.print_exc()
            logging.error(error)
            if error.response['Error']['Code'] == 'LimitExceededException':
                logging.warn('API call limit exceeded; exiting')
                self.user.environment.reached_end = True
                self.user.environment.runner.quit()
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            first_token_metadata["exception"] = e
            last_token_metadata["exception"] = e
        events.request.fire(**first_token_metadata)
        events.request.fire(**last_token_metadata)

    def get_first_string(self, response):
        try:
            stream = response.get('body')
            logging.debug("Stream response:%s", stream)
            i = 1
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_obj = json.loads(chunk.get('bytes').decode())
                        logging.debug("Iterating response no %s : %s", str(i), chunk)
                        text = get_next_function(chunk_obj)
                        self.final_output.append(text)
                        if text and text != '\n' and len(text) != 0:
                            logging.info("First token: %s", text)
                            return text
                        i += 1
        except StopIteration:
            print("done")

    def drain_stream(self, response):
        response_str = ""
        try:
            stream = response.get('body')
            logging.debug("Stream response:%s", stream)
            next_res = ""
            i = 1
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_obj = json.loads(chunk.get('bytes').decode())
                        logging.debug("Iterating response no %s : %s", str(i), chunk_obj)
                        next_res = get_next_function(chunk_obj)
                        self.final_output.append(next_res)
                        if next_res is not None:
                            self.final_output.append(get_next_function(chunk_obj))
                        i += 1
            logging.info("Last token: %s", next_res)
            logging.info(self.final_output)
        except StopIteration:
            logging.info(response_str)
            logging.error("done")
            return


class BotoUser(FastHttpUser):
    abstract = True

    def __init__(self, env):
        self.host = "http://localhost:8888"
        super().__init__(env)
        self.client = BotoClient(self.host)


class MyUser(BotoUser):
    @task
    def send_request(self):
        self.client.send()


##Write main program to test BotoClient
if __name__ == "__main__":
    ##Set environment HOST to the endpoint name
    # os.environ["HOST"] = "meta.llama2-13b-chat-v1"
    # os.environ["REGION"] = "us-east-1"
    # os.environ["CONTENT_TYPE"] = "application/json"
    # os.environ["PAYLOAD_FILE"] = "chat.txt"
    # os.environ["MAX_NEW_TOKENS"] = "500"
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting locust script")
    logging.info("MODEL_ID=%s", os.environ["ENDPOINT_NAME"])
    logging.info("REGION=%s", os.environ["REGION"])
    logging.info("PAYLOAD_FILE=%s", os.environ["PAYLOAD_FILE"])
    logging.info("MAX_NEW_TOKENS=%s", os.environ["MAX_NEW_TOKENS"])
    client = BotoClient(os.environ["HOST"])
    client.send()
