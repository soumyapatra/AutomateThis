
import csv
#csv.register_dialect('mydialect',delimiter=',',skipinitialspace=True)

with open("./sample.txt","rt") as csvFile:
   reader=csv.reader(csvFile, delimiter='o')
   for lines in reader:
       print(lines)
