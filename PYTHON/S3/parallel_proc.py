import multiprocessing
import time


def square(x):
    return x * x


list123 = [1, 56, 43, 24, 2, 5, 546, 2, 34, 564, 7, 321, 5, 667, 343, 213, 23, 24, 53, 6, 76, 12, 231, 31, 5, 3, 564,
           7665, 7, 23, 1, 23123]

if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=10)
    result_async = [pool.apply_async(square, args=(i,)) for i in
                    list123]
    results = [r.get() for r in result_async]
    print("Output: {}".format(results))
