import os
import re
import json
import random
from datetime import datetime
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from PIL import Image, ImageTk
from collections import defaultdict, namedtuple
from functools import partial


Product = None
Part = namedtuple('Part', ('trait_value', 'weight', 'path'))

PATH_PREFIX = './traits'
RESTORE_PREFIX = './assets'
file_dict = None
attribute_dict = defaultdict(list)
selected_attributes_dict = None
image_number = 500
image_name = 'sample'
metadata_template = {
    "name": "",
    "symbol": "",
    "description": "",
    "attributes": [],
    "collection": {
        "name": "",
        "family": "",
    },
    "properties":{
        "files": [
            {
                "uri": "",
                "type": "image/png",
            }
        ],
        "category": "image",
        "creators": [
            {
                "address": "",
                "verified": False,
                "share": ""
            }
        ]
    }
}


def on_select(event):
    w = event.widget
    global selected_attributes_dict

    selected_index = w.curselection()[0]
    print(w.get(selected_index))


def on_load(_root):
    # Init file tree
    global file_dict
    file_dict = defaultdict(list)
    directories = sorted(list(os.listdir(f'{PATH_PREFIX}')), reverse=False)
    for directory in directories:
        if not os.path.isdir(f'{PATH_PREFIX}/{directory}'):
            continue

        files = sorted(list(os.listdir(f'{PATH_PREFIX}/{directory}')), reverse=False)
        for file in files:
            if not re.search(r'\.png$', file):
                continue
            file_dict[directory].append(file)

    # Init attribute tree
    global attribute_dict
    attribute_dict = defaultdict(list)

    traits = []
    for directory, files in file_dict.items():
        trait = re.sub(r'^\d*_', '', directory)
        traits.append(trait)

        for file in files:
            basename = re.sub(r'\.png$', '', file)
            m = re.match(r'([^\s]+)_(\d+)$', basename)
            if m:
                basename = m.group(1)
                weight = int(m.group(2))
            else:
                weight = 10_000

            # {TRAIT: (ATTR_VALUE, WEIGHT, RESOURCE_PATH)}
            attribute_dict[trait].append(
                Part(basename, weight, f'{PATH_PREFIX}/{directory}/{file}')
            )

    # Product named Tuple
    global Product
    Product = namedtuple('Product', traits)

    _right_frame = _root.nametowidget('.make_frame.right_frame')
    _right_frame.pack_forget()
    _right_frame.pack()

    for i, (trait, attrs) in enumerate(attribute_dict.items()):
        # Labal Frame
        lbl_frame = ttk.LabelFrame(
            _right_frame,
            text=trait.capitalize(),
            name=f'{trait}_frame',
            relief='flat',
            borderwidth=0,
        )
        lbl_frame.grid(row=i // 3, column=i % 3, pady=30, padx=15)

        # Entry
        entry = ttk.Entry(lbl_frame, name=f'{trait}_entry', width=15)
        # entry.bind('<KeyRelease>', )
        entry.pack(pady=5)

        # List Box
        listbox = tk.Listbox(
            lbl_frame,
            name=f'{trait}_listbox',
            font=('System', 16),
            borderwidth=0,
            highlightthickness=0,
            width=15,
            selectmode='SINGLE'
        )
        listbox.bind('<<ListboxSelect>>', on_select)
        listbox.pack(padx=5)

        [listbox.insert(tk.END, attr[0]) for attr in attrs]


def on_make(_root):
    global image_number
    global image_name
    global attribute_dict
    global Product

    products = []
    sampling_dict = defaultdict(list)

    for trait, values in attribute_dict.items():
        _, weights, _ = list(zip(*values))
        sampling_dict[trait] = random.choices(values, weights=weights, k=image_number)

    for i in range(image_number):
        temp = {trait: values[i] for trait, values in sampling_dict.items()}
        products.append(Product(**temp))

    print(len(products))
    print(len(set(products)))

    ## products는 완성품 배열

    sample_path = list(attribute_dict.values())[0][0][2]
    sample_img = Image.open(sample_path)
    base_img = Image.new(size=sample_img.size, mode="RGBA")

    # Set restore path
    restore_path = f'{RESTORE_PREFIX}/{datetime.utcnow().strftime("%Y-%m-%d %H%M%SZ")}'
    if not os.path.exists(restore_path):
        os.makedirs(restore_path)

    for i in range(image_number):
        base_metadata = metadata_template.copy()

        for trait, attr in product.items():
            temp_img = Image.open(attr[i][2], mode='r')
            base_img = Image.alpha_composite(base_img, temp_img)

            base_metadata['name'] = f'{image_name} #{i+1}'
            base_metadata['attributes'].append(
                {'trait_type': trait, 'value': attr[i][0]}
            )

        print(base_metadata)
        print([v[0][:2] for v in product.values()])
        # base_tkimg = ImageTk.PhotoImage(base_img)

        base_img.save(f'{restore_path}/{i}.png')
        with open(f'{restore_path}/{i}.json', mode='w', encoding='utf-8') as f:
            json.dump(base_metadata, f)

        # todo
        ## base_tkimg 만들기


if __name__ == '__main__':
    root = tk.Tk(baseName='My PFP', screenName='hello', className='Profile Picture Maker')
    root.geometry('1280x720+100+100')

    style = ttk.Style(root)
    # windows : ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    # osx :
    style.theme_use('alt')
    ttk.Style().configure('Font.TLabelframe', font="50")

    # Frame Option
    # flat, groove, raised, ridge, solid, or sunken
    frame_opt = {
        'borderwidth': 2,
        'relief': 'solid',
    }

    # Make notebook
    notebook = ttk.Notebook(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    notebook.pack()

    # Make Frame
    make_frame = ttk.Frame(root, name='make_frame')
    notebook.add(make_frame, text='MAKE')

    # Analysis Frame
    analysis_frame = ttk.Frame(root, name='analysis_frame')
    notebook.add(analysis_frame, text='Analysis')


    # Left Frame
    make_left_frame = ttk.Frame(make_frame, name='left_frame')
    make_left_frame.pack(side=tk.LEFT)

    # Center Frame
    make_center_frame = ttk.Frame(make_frame, name='center_frame')
    make_center_frame.pack(side=tk.LEFT, ipadx=15)

    # Right Frame
    right_frame = ttk.Frame(make_frame, name='right_frame')
    right_frame.pack(side=tk.LEFT, fill='y')

    # Canvas Widget
    product_canvas = tk.Canvas(make_left_frame, width=500, height=500, name='product_canvas')
    product_canvas.pack()

    # Load Button
    on_load = partial(on_load, root)
    btn_load = ttk.Button(make_center_frame, text="LOAD", command=on_load)
    btn_load.pack(padx=5, pady=10)

    # Make Button
    on_make = partial(on_make, root)
    btn_make = ttk.Button(make_center_frame, text='MAKE', command=on_make)
    btn_make.pack(padx=5, pady=10)

    # Test Button
    def func():
        print(root.winfo_width(), root.winfo_height())

    test_btn = ttk.Button(make_center_frame, text='TEST', command=func)
    test_btn.pack(padx=5, pady=10)

    # analysis_canvas
    analysis_canvas = tk.Canvas(analysis_frame, name='analysis_canvas', width=500, height=500)
    analysis_canvas.pack(side=tk.LEFT)

    btn_load_files = ttk.Button()

    # App run
    root.mainloop()
