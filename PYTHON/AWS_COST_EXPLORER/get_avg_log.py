filename = "access.log"

reader = open(filename, "r")
count = 0
lines = reader.readlines()
avg_time = 0
for i in lines:
    ip = i.split(" ")[0]
    status_code = i.split(" ")[8]
    time = int(i.split(" ")[9])
    #print(status_code)
    if ip == "172.16.0.13" and status_code == "200":
        avg_time = avg_time + time
        count += 1
    total_avg_time = avg_time / count

print(total_avg_time)
