from kafka import KafkaConsumer

consumer = KafkaConsumer('testing3', bootstrap_servers=['localhost:9091', 'localhost:9092', 'localhost:9093'])
for message in consumer:
    topic_name = message.topic
    part = message.partition
    data = message.value.decode("utf-8")
    print(f"Topic: {topic_name}\nPartition: {part}\nmessage: {data}\n\n")
