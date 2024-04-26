import numpy as np


def round_up_to_odd(number: float) -> int:
    """
    Rounds up a given floating point number to the nearest odd integer. If the floating point number
    is already an odd integer, it returns the same number cast as an int.

    :param number: The numerical value to be rounded to the nearest odd integer.
    :type number: float

    :return: The rounded-up odd integer.
    :rtype: int
    """

    return int(np.ceil(number) // 2 * 2 + 1)
