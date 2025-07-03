import csv

x="hi there"
col_header="EventID,SourceIP,User,Region,InstanceID,InstanceType"

with open("./sample","a") as csvFile:
     csvWriter=csv.writer(csvFile)
     csvWriter.writerow(x.split())
