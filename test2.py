import pandas as pd
import glob, json, re


asset_path = './assets/2021-12-21 095638Z'
files = list(glob.glob(f'{asset_path}/*.json'))

data = []
for file in files:
    with open(file, mode='r', encoding='utf-8') as f:
        metadata = json.load(f)

    search = re.search(r'[\/](\d+.json)', file)
    if not search:
        continue

    basename = search.group(1)
    temp = {'file': basename, 'name': metadata['name']}

    for attr_obj in metadata['attributes']:
        temp[('attribute', attr_obj['trait_type'])] = attr_obj['value']

    data.append(temp)

df = pd.DataFrame(data=data)