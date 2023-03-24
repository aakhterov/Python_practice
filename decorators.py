"""

Goals:
1) Understanding mechanism of decorators
2) Testing various decorator

Reference:
1) https://medium.com/towards-data-science/python-decorators-for-data-science-6913f717669a
2) https://medium.com/towards-data-science/12-python-decorators-to-take-your-code-to-the-next-level-a910a1ab3e99

"""

import time
import requests
from requests.exceptions import ConnectionError
from functools import wraps, lru_cache, singledispatch
from dataclasses import dataclass, field


def exec_time(func):
    """

    :param func: function that decorated
    :return: wrapper function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function evaluating execution time
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {(end_time - start_time)}")
        return result
    return wrapper


@exec_time
def test_execution_time(delay: int):
    """
    Simulate heavy calculation
    :param delay: delay in seconds to simulate heavy calculation
    :return: None
    """
    print("Start function")
    time.sleep(delay)
    print("End function")


def repetition_request(repetitions_num: int = 3, delay: int = 2):
    """
    Decorator for request repetitions
    :param repetitions_num: number of repetitions
    :param delay: delay between repetitions
    :return: decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            i = 1
            while i <= repetitions_num:
                try:
                    print(f"Attempt #{i}")
                    result = func(*args, **kwargs)
                    if result.status_code == 404:
                        raise ConnectionError
                    return result
                except ConnectionError as ex:
                    i += 1
                    time.sleep(delay)
            raise ConnectionError
        return wrapper
    return decorator


@repetition_request(repetitions_num=3, delay=2)
def fake_api(url):
    return requests.get(url)


class Person:
    """
    Class for testing @property decorator
    """

    def __init__(self, age: int):
        self.__age = age

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, age):
        if 20 <= age <= 60:
            self.__age = age
        else:
            raise ValueError("Age must be between 20 and 60")


@dataclass(order=True)
class PersonII:
    """
    Class for testing @dataclass decorator
    """
    sort_index: int = field(init=False, repr=False) # special field for sorting
    first_name: str
    last_name: str
    age: int

    def __post_init__(self):
        """
        This function is called after __init__ and sets age field as a field for sorting
        :return: None
        """
        self.sort_index = self.age


def cache(func):
    """
    Decorator for using cache
    :param func: function that decorated
    :return: wrapper function
    """
    cache_dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = ()
        # Convert all mutable types to tuples because dictionary ket must be immutable
        for v in args:
            cache_key += tuple(v) if type(v) in (list, dict, set) else (v,)
        for k, v in kwargs.items():
            cache_key += k, tuple(v) if type(v) in (list, dict, set) else v

        if cache_key not in cache_dict:
            cache_dict[cache_key] = func(*args, **kwargs)
        return cache_dict[cache_key]

    return wrapper


def fibonacci_wo_cache(n):
    """
    Calculate n-th fibonacci number

    :param n: number of fibonacci numbers
    :return: n-th fibonacci number
    """
    if n <= 2:
        return 1
    return fibonacci_wo_cache(n-2) + fibonacci_wo_cache(n-1)


# hand-made cache decorator
@cache
def fibonacci_w_cache(n):
    """
    Calculate n-th fibonacci number

    :param n: number of fibonacci numbers
    :return: n-th fibonacci number
    """
    if n <= 2:
        return 1
    return fibonacci_w_cache(n-2) + fibonacci_w_cache(n-1)


# inbuild cache decorator
@lru_cache
def fibonacci_w_inbuild_cache(n):
    """
    Calculate n-th fibonacci number

    :param n: number of fibonacci numbers
    :return: n-th fibonacci number
    """
    if n <= 2:
        return 1
    return fibonacci_w_cache(n-2) + fibonacci_w_cache(n-1)


def helper_function(func, n):
    """
    Helper function for calculate n-th fibonacci number and execution time and print result

    :param func: function that execution time we count
    :param n: number of fibonacci numbers
    :return: None
    """
    t1 = time.time()
    result = func(n)
    t2 = time.time()
    print(f"{n}-th fibonacci number: {result}. Time without using cache: {(t2-t1)}")


@singledispatch
def func(n: int):
    """
    Function named "func" that get integer number as input and do an operation with it

    :param n: any integer number
    :return: None
    """
    n += 1
    print (f"n is {type(n)}. n = {n}")


@func.register(str)
def _(n: str):
    """
    Function named "func" that get string as input and do an operation with it

    :param n: any string
    :return: None
    """
    n += "_postfix"
    print (f"n is {type(n)}. n = {n}")


@func.register(list)
def _(n: list):
    """
    Function named "func" that get list as input and do an operation with it

    :param n: any list
    :return: None
    """
    n.append(1)
    print (f"n is {type(n)}. n = {n}")


if __name__ == "__main__":
    print(f"1. Print function execution time")
    test_execution_time(1)
    print("="*10)

    print(f"2. Try to request valid and invalid url")
    valid_url = "https://google.com/"
    invalid_url = "https://mos1.ru/"
    try:
        result = fake_api(invalid_url)
        print(f"Status code: {result.status_code}")
    except ConnectionError as ex:
        print("ConnectionError")
    print("="*10)

    print(f"3. @property decorator")
    p1 = Person(25)
    print(f"Current age: {p1.age}")
    p1.age = 40
    try:
        p1.age = 80
    except ValueError as ex:
        print(f"{ex.__class__.__name__}: {ex}")
    print("="*10)

    print(f"4. @dataclass decorator")
    p1 = PersonII(first_name="Alex", last_name="Smith", age=25)
    p2 = PersonII(first_name="John", last_name="Ivanovich", age=45)
    print(f"Person one p1: {p1}")
    print(f"Person two p2: {p2}")
    print(f"Сomparison of two Person instances p1 and p2 using field age: p1<p2 - {(p1<p2)}")
    print("="*10)

    print(f"5. Calculate n-th fibonacci number with and without using cache")
    n = 30
    helper_function(fibonacci_wo_cache, n)
    helper_function(fibonacci_w_cache, n)
    helper_function(fibonacci_w_inbuild_cache, n)
    print("="*10)

    print(f"6. \"Polymorphism\" (same interface for different input types)")
    n_int = 10
    n_str = "hello"
    n_list = [1,2]

    func(n_int)
    func(n_str)
    func(n_list)
    print("="*10)

