from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="localhost:9092")
for i in range(0, 200):
    producer.send("test1", b"Hi There. this is {i}")
