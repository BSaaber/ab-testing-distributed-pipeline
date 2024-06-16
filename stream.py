# ~/big_data/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 --jars ~/big_data/spark_modules/clickhouse-jdbc-0.5.0-shaded.jar  ~/Documents/work/ab_testing_from_scratch/spark_streaming_read_data_from_kafka.py localhost 9999

# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 --jars clickhouse-jdbc.jar stream.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col
from pyspark.sql.functions import split
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StringType, IntegerType, BooleanType
import logging

spark = SparkSession.builder.appName('sparkStructuredStreamingWordCount').getOrCreate()

input_schema = StructType() \
        .add('session_id', StringType()) \
        .add('logs', StringType()) \
        .add('testids', StringType()) \
        .add('datetime', StringType())

IN_DOCKER = True

data = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092,kafka2:9093" if IN_DOCKER else "localhost:29092,localhost:29093") \
    .option("subscribe", "test") \
    .load()

data = data.selectExpr("CAST(value AS STRING)", "timestamp")

logging.error('FUCK THIS FUCK')
print('\n\n\nthis is data schema:\n')
data.printSchema()
print('\n\n\n')

parsed_data = data.select(from_json(col("value").cast("string"), input_schema).alias("preparsed_value"))

parsed_data = parsed_data.select("preparsed_value.*").alias('parsed_value')
print('\n\n\nthis is parsed_data schema:\n')
parsed_data.printSchema()
print('\n\n\n')

parsed_data = parsed_data.select(
    explode(
        split(parsed_data.testids, ',')
    ).alias('testid'),
    col('session_id'),
    col('logs'),
    col('datetime'),
)

parsed_data.createOrReplaceTempView("parsed_value")

result = spark.sql("SELECT session_id, CAST(testid as INT), datetime, IF(logs LIKE '%purchase confirmed%', TRUE, FALSE) as is_purchased FROM parsed_value")

result = result.filter('testid is not null')


def batch_write(batch_df, batch_id):
    print('starting batch')

    # username instead of user?

    batch_df.write \
        .mode('append')\
        .format('jdbc') \
        .option('url', 'jdbc:clickhouse://{}:8123/default'.format('clickhouse-server' if IN_DOCKER else 'localhost')) \
        .option('user', 'admin').option('password', 'admin') \
        .option('driver', 'com.clickhouse.jdbc.ClickHouseDriver') \
        .option('dbtable', 'log_testid_data') \
        .save()

    # df.show()
    print('end of processing batch')


query = result.writeStream \
    .foreachBatch(batch_write) \
    .trigger(processingTime='5 seconds') \
    .start()

query.awaitTermination()

# query = result.writeStream.format('console')\
#     .outputMode('append') \
#     .start()
#
# query.awaitTermination()
