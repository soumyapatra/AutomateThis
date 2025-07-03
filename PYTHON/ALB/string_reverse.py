
string1 = "anything"
revered_string = ""
string_len = len(string1)

i = len(string1) - 1
while i >= 0:
    revered_string = revered_string + string1[i]
    i = i - 1

print(revered_string)