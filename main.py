from flask import Flask
from flask import request
from flask import Response

from amazon_bs import scrape

# from secrets import makeKey
import os
import json

app = Flask(__name__)

# makeKey()

k = os.environ["KEY"]


@app.route("/<key>")
def parse(key):
    print("Started")
    if k == key:
        print("keys are matching")
        q_key = request.args.get("key").replace(" ", "+")
        q_page = request.args.get("page")
        results = scrape(q_key, q_page)
        return Response(
            "{'results': {res}}".format(res=results),
            status=200,
            mimetype="application/json",
        )
    else:
        results = None
        return Response(
            "{'results': {res}}".format(res=results),
            status=404,
            mimetype="application/json",
        )

