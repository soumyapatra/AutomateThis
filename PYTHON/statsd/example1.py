import statsd
import sys
from random import random
from random import seed
import time

# seed(1)
ip = "10.24.73.140"


def say_hi(word):
    return "HI {}".format(word)


if len(sys.argv) != 2:
    print("Please specify args")
    exit()
else:
    while True:
        result = say_hi(sys.argv[1])
        c = statsd.StatsClient(ip, 8125, prefix='bar')
        c.incr('foo-local')
        a = statsd.StatsClient(ip, 8125, prefix='val')
        value = random()
        print(value)
        a.set('random_val', value)
        print(result)
