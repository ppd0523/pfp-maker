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
image_number = 50
image_name = 'sample'


def on_select(event):
    w = event.widget
    global selected_attributes_dict

    selected_index = w.curselection()[0]
    print(w.get(selected_index))


def on_load(ctx):
    print(ctx)
    ctx['state'] = tk.DISABLED
    ctx['text'] = 'LOADED'

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
        traits.append(trait)  # parsed directories

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
    Product = namedtuple('Product', traits)  # head, eyes, mouth

    # _right_frame = _root.nametowidget('.make_frame.right_frame')
    # _right_frame.pack_forget()
    # _right_frame.pack()

    # for i, (trait, attrs) in enumerate(attribute_dict.items()):
    #     # Labal Frame
    #     lbl_frame = ttk.LabelFrame(
    #         _right_frame,
    #         text=trait.capitalize(),
    #         name=f'{trait}_frame',
    #         relief='flat',
    #         borderwidth=0,
    #     )
    #     lbl_frame.grid(row=i // 3, column=i % 3, pady=30, padx=15)
    #
    #     # Entry
    #     entry = ttk.Entry(lbl_frame, name=f'{trait}_entry', width=15)
    #     # entry.bind('<KeyRelease>', )
    #     entry.pack(pady=5)
    #
    #     # List Box
    #     listbox = tk.Listbox(
    #         lbl_frame,
    #         name=f'{trait}_listbox',
    #         font=('System', 16),
    #         borderwidth=0,
    #         highlightthickness=0,
    #         width=15,
    #         selectmode='SINGLE'
    #     )
    #     listbox.bind('<<ListboxSelect>>', on_select)
    #     listbox.pack(padx=5)
    #
    #     [listbox.insert(tk.END, attr[0]) for attr in attrs]


def on_make(ctx):
    global image_number
    global image_name
    global attribute_dict
    global Product

    ctx['state'] = tk.DISABLED
    ctx['text'] = 'MADE'

    products = []
    sampling_dict = defaultdict(list)

    for trait, values in attribute_dict.items():
        _, weights, _ = list(zip(*values))
        sampling_dict[trait] = random.choices(values, weights=weights, k=image_number)

    for i in range(image_number):
        temp = {trait: values[i] for trait, values in sampling_dict.items()}
        products.append(Product(**temp))

    print('before: ',len(products))
    products = list(set(products))
    print('after: ', len(products))
    ## products는 완성품 배열

    sample_path = products[0][0].path
    sample_img = Image.open(sample_path)

    # Set restore path
    restore_path = f'{RESTORE_PREFIX}/{datetime.utcnow().strftime("%Y-%m-%d %H%M%SZ")}'
    if not os.path.exists(restore_path):
        os.makedirs(restore_path)

    # Load metadata.json template
    with open('./metadata.json', mode='r') as f:
        metadata_template = json.load(f)

    for i, prod in enumerate(products):
        base_metadata = metadata_template.copy()
        base_img = Image.new(size=sample_img.size, mode='RGBA')

        for trait_type, part in prod._asdict().items():
            part_img = Image.open(part.path, mode='r')
            base_img = Image.alpha_composite(base_img, part_img)
            base_metadata['attributes'].append(
                {'trait_type': trait_type, 'trait_value': part.trait_value}
            )
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
    notebook = ttk.Notebook(root, name='notebook', width=root.winfo_screenwidth(), height=root.winfo_screenheight())
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
    product_canvas = tk.Canvas(make_left_frame, width=500, height=500, name='make_canvas')
    product_canvas.pack()

    # Load assets Button
    # on_load = partial(on_load, root)
    # btn_load = ttk.Button(make_center_frame, name='btn_load', text="LOAD ASSETS", command=on_load)
    btn_load = ttk.Button(make_center_frame, name='btn_load', text="LOAD ASSETS")
    btn_load['command'] = partial(on_load, btn_load)
    btn_load.pack(padx=5, pady=10)

    # Make Button
    btn_make = ttk.Button(make_center_frame, name='btn_make', text='MAKE IMAGE')
    btn_make['command'] = partial(on_make, btn_make)
    btn_make.pack(padx=5, pady=10)

    # Test Button
    def func():
        print(root.winfo_width(), root.winfo_height())

    test_btn = ttk.Button(make_center_frame, text='TEST', command=func)
    test_btn.pack(padx=5, pady=10)

    # analysis_canvas
    analysis_canvas = tk.Canvas(analysis_frame, name='analysis_canvas', width=500, height=500)
    analysis_canvas.pack(side=tk.LEFT)

    # App run
    root.mainloop()
