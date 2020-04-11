from random import randint

def roll(*args, get_sum=True):
    nargs = len(args)

    if nargs == 0:
        rolls = [randint(1, 6)]
    elif nargs == 1:
        arg = args[0]
        if isinstance(arg, str):
            num, sides = (int(i) for i in arg.split('d'))
            rolls = [randint(1, sides) for _ in range(num)]
        elif isinstance(arg, int):
            rolls = [randint(1, 6) for _ in range(num)]
        else:
            raise ValueError('Invalid dice input')
    elif nargs == 2:
        num, sides = args
        rolls = [randint(1, sides) for _ in range(num)]
    else:
        raise ValueError('Invalid dice input')

    if get_sum:
        return sum(rolls)
    return rolls