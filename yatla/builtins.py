def RoundUp(val, base):
    return val + (base - val) % base


def RoundDown(val, base):
    return val - (val % base)


def Minimum(val1, val2):
    return min(val1, val2)


def Maximum(val1, val2):
    return max(val1, val2)
