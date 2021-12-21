from enum import Enum
from typing import Tuple


class Color(str, Enum):
    black = '#000000'
    white = '#FFFFFF'


def _ratio(size: Tuple[int, int]) -> float:
    """
    (height/width) ratio
    :param size: (width, height)
    :return: ratio
    """
    return size[1] / size[0]


def rescale(size: Tuple[int, int], max_size: Tuple[int, int]) -> Tuple[int, int]:
    ratio = _ratio(size)
    wx = max_size[0] / (ratio * size[0])
    hx = max_size[1] / (ratio * size[1])



if __name__ == '__main__':
    size = (128, 64)
    max_size = (300, 300)
    r = _ratio(size)
    print(r)