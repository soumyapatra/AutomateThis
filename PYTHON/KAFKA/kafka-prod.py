from kafka import KafkaProducer
import time

bootstrap_servers = ['localhost:9091', 'localhost:9092', 'localhost:9093']
topicName = 'testing3'

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

for i in range(0, 100):
    key1 = "key1"
    message = f"this is message{i} from key"
    data1 = message.encode("utf-8")

    producer.send(topicName, f"this is message{i} for key1".encode("utf-8"), "key1".encode("utf-8"))
    producer.send(topicName, f"this is message{i} for key2".encode("utf-8"), "key2".encode("utf-8"))
    time.sleep(1)
    producer.flush()
