# read sample_sentences.txt

import datetime
import json
# file I/O
import os
import time
import requests

# read sample_sentences.txt (relative directory)
raw_sample_sentences = open(os.path.join(os.path.dirname(__file__), "sample_sentences.txt"), "r")
sample_sentences = raw_sample_sentences.read().split("\n")
output = ""

def get_cefr_level(sentence):
    # send post request to http://localhost:8000/analyze/cefr/
    url = "http://127.0.0.1:3000/analyze/cefr/"

    data = {
        "content": sentence
    }

    # send post request
    response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

    response_json = response.json()

    return response_json["meta"]["grade"]

def save_output():
    # timestamp as int
    timestamp = int(datetime.datetime.now().timestamp())

    filename = "output_" + str(timestamp) + ".txt"

    with open(os.path.join(os.path.dirname(__file__), filename), "w") as output_file:
        output_file.write(output)

def initiate():
    global output
    for sentence in sample_sentences:
        cefr_result = get_cefr_level(sentence)
        print(f"{sentence} -> {cefr_result}")
        output += cefr_result + "\n"
        # wait for 0.5 seconds before sending another request
        time.sleep(0.01)
    save_output()

initiate()