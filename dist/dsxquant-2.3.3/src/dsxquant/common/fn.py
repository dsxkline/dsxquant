
import random
import time


def create_unique_id():
    t = time.time_ns() + random.randint(0,100000)
    return t