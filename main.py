import os

from pyspark import SparkContext

base_path = os.path.dirname(os.path.realpath(__file__)) + '/'
text_morphine_path = base_path + 'morphine.txt'
text_map_result_path = base_path + 'map_result'
text_reduce_result_path = base_path + 'reduce_result'

sc = SparkContext('local', 'Simple WordCount on one machine')

words = sc.textFile(text_morphine_path).flatMap(lambda text: text.lower().replace('.', '').replace(',', '').split(' '))

result = words.map(lambda word: (word, 1))\
    .reduceByKey(lambda a, b: a + b)\
    .sortBy(lambda a: a[1], ascending=False)
result.saveAsTextFile(text_map_result_path)

