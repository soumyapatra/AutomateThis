import random

num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]


def return_guess(select, list, result):
    result = random.choice(list)
    if select not in list:
        return f'Please select number between 1 to 20'
    else:
        if select > result:
            print(f'Select a greater number')


result = random.choice(num_list)
print(result)
num = input("Guess a Number between 1 to 20: ")

if num not in num_list:
    print()

print("Correct Guess")