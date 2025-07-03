import sys

filename = sys.argv[0]

if len(sys.argv) < 1:
    print("No argument passed")

data = open(filename).read().splitlines()
print(data)