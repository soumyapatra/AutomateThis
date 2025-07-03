import re

string = "vpc-17b7a075"

ab = re.compile("^eni-\w*")
if ab.match(string):
    print("true")