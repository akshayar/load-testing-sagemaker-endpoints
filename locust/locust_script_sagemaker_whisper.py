import json
import logging
import os
import time
import traceback
import gevent.monkey

gevent.monkey.patch_all()

import boto3
from botocore.config import Config
from locust.contrib.fasthttp import FastHttpUser

from locust import task, events

region = os.environ["REGION"]
payload_file = os.environ["PAYLOAD_FILE"]
payload = None
# Read file into memory
with open(payload_file, 'rb') as f:
    payload = f.read()


class BotoClient:
    def __init__(self, host):
        # Consider removing retry logic to get accurate picture of failure in locust
        config = Config(
            region_name=region, retries={"max_attempts": 0, "mode": "standard"}
        )
        self.sagemaker_client = boto3.client("sagemaker-runtime", config=config)
        self.endpoint_name = host
        # Log the details above
        logging.debug("endpoint_name=%s, payload_file=%s", self.endpoint_name, payload_file)

    def send(self):
        request_meta = {
            "request_type": "InvokeEndpoint",
            "name": "SageMakerWhisper",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        start_perf_counter = time.perf_counter()
        string_len = 1

        try:
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                Body=payload
            )
            response_string = json.loads(response['Body'].read().decode())
            logging.debug("Response Body:%s", response_string)
            logging.info("Generated String:%s", response_string)
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            request_meta["exception"] = e

        response_time_ms = (time.perf_counter() - start_perf_counter) * 1000
        request_meta["response_time"] = response_time_ms
        logging.info("response_time_ms=%s", str(response_time_ms))
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting locust script")
    logging.info("HOST=%s", os.environ["HOST"])
    logging.info("REGION=%s", os.environ["REGION"])
    logging.info("PAYLOAD_FILE=%s", os.environ["PAYLOAD_FILE"])
    client = BotoClient(os.environ["HOST"])
    client.send()
