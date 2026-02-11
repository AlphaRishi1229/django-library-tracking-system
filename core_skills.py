import random
# rand_list =

rand_list = [random.randint(1, 20) for _ in range(10)]

# list_comprehension_below_10 =
list_comprehension_below_10 = [i for i in rand_list if i < 10]

# list_comprehension_below_10 =
def filter_less_than_num(n: int) -> bool:
    """Returns true if number is less than 10"""
    if n < 10:
        return True
    return False

list_comprehension_below_10 = [i for i in filter(filter_less_than_num, rand_list)]
