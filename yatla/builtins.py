"""
Built-in functions accessible from a template.
"""


def RoundUp(val, base):
    """
    Returns the smallest multiple of base that is greater than or equal to val. This is
    effectively rounding val up to the first factor of base.
    """
    return val + (base - val) % base


def RoundDown(val, base):
    """
    Returns the greatest multiple of base that is less than or equal to val. This is
    effectively rounding val down to the first factor of base.
    """
    return val - (val % base)


def Minimum(val1, val2):
    """
    Returns the smallest of val1 and val2.
    """
    return min(val1, val2)


def Maximum(val1, val2):
    """
    Returns the greatest of val1 and val2.
    """
    return max(val1, val2)
