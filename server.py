from flask import Flask, request, jsonify, Response
import os
import threading
import time
import scraper
import json

app = Flask(__name__)
DATA = {}


def init_get_data():
    global DATA
    data = {}
    # try:
    scraper.main()
    # except:
    #     print('data not updated')
    try:
        with open('./series.json', 'r') as f:
            text = f.read()
            data = json.loads(text)['data']
            f.close()
    except:
        print('No data found.')
    DATA = data


@app.route('/GET_DATA/')
def returnSeries():
    return jsonify(DATA)


# @app.route('/ADD_SERIES/',method = ['POST'])
# def addSeries():
#     with open('./series.json', 'w') as f:
#         DATA = {}
#         res = f.read()
#         return json.parse(res)

# @app.route('/new_series/',method= ['POST'])
# def get_new_series():
#     data = request.form


@app.route('/TEST/')
def test():
    return "<H1>WORKS</H1>"


if __name__ == "__main__":
    init_get_data()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
