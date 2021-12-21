import pandas as pd

data = {
    'A': [1, 2, 3],
    ('B', 'aa'): [10, 20, 30],
    ('B', 'bb'): [100, 200, 300],
}

df = pd.DataFrame(data=data)


print(df.head())

