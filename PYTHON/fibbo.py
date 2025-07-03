def get_fibbo(x):
    if x == 0:
        return 0
    if x == 1:
        return 1
    else:
        return (get_fibbo(x-1) + get_fibbo(x-2))

num=int(input("Enter Number"))

for i in range(num+1):
    print(get_fibbo(i))

