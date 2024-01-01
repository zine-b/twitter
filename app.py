import ast
from collections import OrderedDict

from flask import Flask, jsonify, request
from flask import render_template

import logging
from utils import read_one_block_of_yaml_data

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


app = Flask(__name__)

dataValues = []
categoryValues = []

tags = {}

properties = {}

def get_top_players(data, n=20):
    """Get top n players by score.
    Returns a dictionary or an `OrderedDict` if `order` is true.
    """
    top = sorted(data.items(), key=lambda x: x[1], reverse=True)[:n]
    return OrderedDict(top)


@app.route("/")
def home():
    return render_template('index.html', dataValues=dataValues, categoryValues=categoryValues)


@app.route('/refreshData')
def refresh_data():
    global dataValues, categoryValues
    return jsonify(dataValues=dataValues, categoryValues=categoryValues)


@app.route('/updateData', methods=['POST'])
def update_data():
    global tags, dataValues, categoryValues

    data = ast.literal_eval(request.data.decode("utf-8"))

    tags[data['hashtag']] = data['count']
    sorted_tags = get_top_players(tags)

    categoryValues.clear()
    dataValues.clear()
    categoryValues = [x for x in sorted_tags]
    dataValues = [tags[x] for x in sorted_tags]

    return "success", 201


if __name__ == "__main__":
    properties = read_one_block_of_yaml_data('local-properties.yml')
    app.run(host=properties['flask']['host'], port=properties['flask']['port'], debug=True)
