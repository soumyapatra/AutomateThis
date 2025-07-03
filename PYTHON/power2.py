def pwer_2(x):
    lst=list(map(lambda x:2**x,range(x)))
    for i in range(x):
        print("2 to the power {} is {}".format(i,lst[i]))

pwer_2(10)
