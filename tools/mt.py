
def num_digit(x):
    re = 0
    if x >= 1:
        re = 0
    if x < 1:
        m = 1 / x
        n = 1
        while m // 10 > 0:
            n = n + 1
            m = m / 10
        re = n
    return re