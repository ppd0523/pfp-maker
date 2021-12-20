from collections import namedtuple

Part = namedtuple('Part', ('head', 'eyes', 'mouth'))

part = Part('big', 'red', 'small')

print(part._asdict())

