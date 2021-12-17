from collections import namedtuple
import json

Point = namedtuple('Point', ('x', 'y'))

p1 = Point(1, 2)
p2 = Point(1, 2)
p3 = Point(1, 3)
print(p1)
print(p2)

print(set([p1, p2, p3]))

import re

p = re.compile(r'.png')

m = p.sub('', 'abc.png')
print(m)