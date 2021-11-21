import os

import pyspark
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split

from utils import read_one_block_of_yaml_data
properties = {}

def send_data(tags: dict) -> None:
    url = properties['flask']['api-url'] + '/updateData'
    response = requests.post(url, json=tags)


def process_row(row: pyspark.sql.types.Row) -> None:
    tags = row.asDict()
    send_data(tags)

def new():
    spark = SparkSession.builder.appName("SparkTwitterAnalysis").getOrCreate()

    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    lines = spark.readStream.format("socket").option("host", properties['spark']['host']).option("port", properties['spark']['port']).load()

    words = lines.select(explode(split(lines.value, " ")).alias("hashtag"))


    wordCounts = words.groupBy("hashtag").count()

    query = wordCounts.writeStream.foreach(process_row).outputMode('Update').start()

    query.awaitTermination()


if __name__ == '__main__':
    try:
        properties = read_one_block_of_yaml_data('local-properties.yml')
        new()
    except BrokenPipeError:
        exit("Pipe Broken, Exiting...")
    except KeyboardInterrupt:
        exit("Keyboard Interrupt, Exiting..")
    except Exception as e:
        exit("Error in Spark App")
