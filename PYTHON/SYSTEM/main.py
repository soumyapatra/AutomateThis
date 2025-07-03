import os
stream = os.popen('ls -al')
output = stream.read()
print(output.split())
