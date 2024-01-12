import os

from utils import read_one_block_of_yaml_data

properties = read_one_block_of_yaml_data('local-properties.yml')

shell = """
#!/bin/bash

export PYSPARK_PYTHON=python3.7
export SPARK_LOCAL_HOSTNAME=localhost
java -jar wiremock/wiremock-standalone-3.3.1.jar --root-dir  wiremock &
$PYSPARK_PYTHON ./twitter_app.py -p 10000 -k "gaming android climate corona bitcoin chatgpt metavers" -m 50 -s 0.01 &
$PYSPARK_PYTHON ./app.py &
$PYSPARK_PYTHON -m webbrowser {} &
$PYSPARK_PYTHON ./spark_app.py
""".format(properties['flask']['api-url'])

os.system(shell)
