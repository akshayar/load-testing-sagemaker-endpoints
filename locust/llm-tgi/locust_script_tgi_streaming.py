import logging
import os
import random
import time
import traceback
from huggingface_hub import InferenceClient
from locust import task, events
from locust.contrib.fasthttp import FastHttpUser

payload_file = os.environ["PAYLOAD_FILE"]
max_new_tokens = os.environ["MAX_NEW_TOKENS"]
min_latency=50

sampPayloads = []
with open(payload_file, "r") as f:
    sampPayloads = f.read().splitlines()


class HuggingFaceTGIClient:
    def __init__(self, host):
        self.tgi_client = InferenceClient(model=host)
        self.max_new_tokens = int(max_new_tokens)
        self.prompt = random.choice(sampPayloads)
        logging.debug("host=%s, prompt=%s, max_new_tokens:%s", host, self.prompt, self.max_new_tokens)

    def send(self):
        first_token_metadata = {
            "request_type": "FirstToken",
            "name": "HF_TGI",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        last_token_metadata = {
            "request_type": "LastToken",
            "name": "HF_TGI",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        try:
            logging.debug("Prompt:%s", self.prompt)
            start_perf_counter = time.perf_counter()
            token = self.tgi_client.text_generation(prompt=self.prompt, max_new_tokens=self.max_new_tokens, stream=True)
            response_time_ms = (time.perf_counter() - start_perf_counter) * 1000
            logging.info("Prompt: %s | Generated String:%s", self.prompt, token)
            count = 1
            for i in token:
                logging.debug("Generated String:%s", i)
                if count == 1:
                    first_token_metadata["response_time"] = (time.perf_counter() - start_perf_counter) * 1000
                count += 1
            last_token_metadata["response_time"] = (time.perf_counter() - start_perf_counter) * 1000
            diff=last_token_metadata["response_time"]-first_token_metadata["response_time"]
            if diff<=5:
                logging.info("Error response as diff=%s", str(diff))
                raise Exception("Error response as diff=%s", str(diff))
            logging.info("response_time_first_token_ms=%s | response_time_last_token_ms=%s",str(first_token_metadata["response_time"]), str(last_token_metadata["response_time"]))
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            first_token_metadata["exception"] = e
            last_token_metadata["exception"] = e
        events.request.fire(**first_token_metadata)
        events.request.fire(**last_token_metadata)


class BotoUser(FastHttpUser):
    abstract = True

    def __init__(self, env):
        super().__init__(env)
        self.client = HuggingFaceTGIClient(self.host)


class MyUser(BotoUser):
    @task
    def send_request(self):
        self.client.send()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting locust script")
    logging.info("HOST=%s", os.environ["HOST"])
    logging.info("CONTENT_TYPE=%s", os.environ["CONTENT_TYPE"])
    logging.info("PAYLOAD_FILE=%s", os.environ["PAYLOAD_FILE"])
    logging.info("MAX_NEW_TOKENS=%s", os.environ["MAX_NEW_TOKENS"])
    client = HuggingFaceTGIClient(os.environ["HOST"])
    client.send()
