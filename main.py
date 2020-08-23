from flask import Flask
from flask import request

from amazon_bs import scrape

# from secrets import makeKey
import os
import json

app = Flask(__name__)

# makeKey()

k = os.environ["KEY"]


@app.route("/<key>")
def parse(key):
    if k == key:
        q_key = request.args.get("key")
        q_page = request.args.get("page")
        results = scrape(q_key, q_page)
    else:
        results = None
    return {"results": results}

