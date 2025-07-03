from kafka import KafkaConsumer
from kafka.structs import TopicPartition
topic = "testing3"

consumer = KafkaConsumer(topic,  bootstrap_servers=['localhost:9091', 'localhost:9092', 'localhost:9093'], auto_offset_reset='earliest')

partitions = consumer.partitions_for_topic(topic)
print("Partition:", partitions)

first_topic_part = TopicPartition(topic, 0)
print("first topic part", first_topic_part)


for message in consumer:
    topic_name = message.topic
    part = message.partition
    data = message.value.decode("utf-8")
    print(f"Topic: {topic_name}\nPartition: {part}\nmessage: {data}\n\n")

