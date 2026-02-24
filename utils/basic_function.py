import random

def get_random_code():
    code_list = list()
    for i in range(6):
        num = random.randint(0, 9)
        code_list.append(str(num))

    return "".join(code_list)