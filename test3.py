from itertools import product

d = [('a', 'b', 'c'), (1, 2, 3), ('aa', 'bb', 'cc')]

p = product(*d)

print(list(p))