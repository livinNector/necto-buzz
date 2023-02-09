import random
import string
from time import sleep
from functools import wraps

def generate_at_interval(interval):
    def generate(func):
        @wraps(func)
        def inner(*args,**kwargs):
            for i in range(5):
                yield func(*args,**kwargs)
                sleep(interval)
        return inner
    return generate


@generate_at_interval(.1)
def random_number_generator():
    return int(random.random()*100)

@generate_at_interval(1)
def random_text_generator(length = 5):
    return "".join(random.choices(string.ascii_lowercase,k=length))

def random_expression_generator(length=3,digits=1,symbols = "+-"):
    numbers = [str(int(random.random()*10**digits)) for _ in range(length)]
    chosen_symbols = random.choices(list(symbols),k=length-1)
    all = [0]*(2*length-1)
    all[::2]=numbers
    all[1::2]=chosen_symbols
    return "".join(all)






if __name__ == "__main__":
    for i in random_expression_generator(5):
        print(i)
