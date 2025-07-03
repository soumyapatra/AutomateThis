import os
import subprocess
import urllib.parse

#subprocess.call("ls")

query = 'sum(kafka_topic_partition_in_sync_replica) by (topic,instance) < 3'
formatted_query = urllib.parse(query)

#subprocess.call(['./nagitheus','-H','http://10.80.120.108:9090', '-q', query,'-c','1', '-m','le','-w','1','-d','yes'])

#result = subprocess.check_output(['./nagitheus','-H','http://10.80.120.108:9090', '-q', query,'-c','1', '-m','le','-w','1','-d','yes'])

cp = subprocess.run(['./nagitheus','-H','http://10.80.120.108:9090', '-q', query,'-c','1', '-m','le','-w','1','-d','yes'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print(cp.stdout)

print(cp.returncode)

