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


def get_env_or_default(env_name, default_value):
    if env_name in os.environ:
        return os.environ[env_name]
    else:
        return default_value


def wait_to_managed_throttling():
    time.sleep(10)


def get_response_llama(response_body):
    return response_body.get('generation')


def get_next_llama(chunk_obj):
    if 'generation' in chunk_obj:
        return chunk_obj['generation'].strip()


def get_next_mistral(chunk_obj):
    if 'outputs' in chunk_obj:
        for jsont in chunk_obj['outputs']:
            return jsont['text']


def get_next_anthropic(chunk_obj):
    content_type = chunk_obj['type']
    if content_type == 'content_block_delta':
        res = chunk_obj['delta']['text']
        return res
    # bytes_json = json.loads(chunk_obj['bytes'])
    # if 'delta' in bytes_json:
    #     return bytes_json['delta']['text']
    # else:
    #     logging.error("No response")
    #     logging.info(chunk_obj)



def get_response_mistral(response_body):
    contents = response_body.get('outputs')
    for content in contents:
        return content['text']


def get_response_anthropic(response_body):
    contents = response_body.get('content')
    for content in contents:
        return content['text']


def find_response_function(model_id):
    if 'mistral' in model_id:
        return get_response_mistral
    elif 'anthropic.claude' in model_id:
        return get_response_anthropic
    else:
        return get_response_llama


def find_get_next_function(model_id):
    if 'mistral' in model_id:
        return get_next_mistral
    elif 'anthropic.claude' in model_id:
        return get_next_anthropic
    else:
        return get_next_llama


def generate_payload(model_id, prompt, max_new_tokens, temperature):
    if 'mistral' in model_id:
        return json.dumps({"prompt": prompt,
                           "max_tokens": max_new_tokens,
                           "temperature": float(temperature)
                           })
    elif 'anthropic.claude' in model_id:
        return json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_new_tokens,
            "system": "Please respond",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            "temperature": float(temperature),
        })
    else:
        return json.dumps({"prompt": prompt,
                           "max_gen_len": max_new_tokens,
                           "temperature": float(temperature)
                           })
