import sentry_sdk
sentry_sdk.init("http://9a3b358763b245939a95091e5f2cef6c@10.80.110.195:8080/1")

try:
    division_by_zero = 1 / 0
except Exception as e:
    print(e)