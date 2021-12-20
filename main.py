import os, sys, platform

if getattr(sys, 'frozen', False):
    _path = sys.excutable
else:
    _path = __file__

os.chdir(os.path.dirname(os.path.abspath(_path)))
import re, json, random
from datetime import datetime
import tkinter as tk
from widget import EntryWithPlaceholder, ScrolledTextWithPlaceholder
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


def on_select(event):
    w = event.widget
    global selected_attributes_dict

    selected_index = w.curselection()[0]
    print(w.get(selected_index))


def on_load(ctx):
    ctx['state'] = tk.DISABLED
    ctx['text'] = 'LOADED'

    ctx.master.children['btn_shuffle']['state'] = tk.NORMAL

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

    # _right_frame = ctx.master.master.nametowidget('.make_frame.right_frame')
    # _right_frame
    # _right_frame.pack()
    #
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
    global attribute_dict
    global Product

    image_number = ctx.master.getvar('image_num_var')
    image_name = ctx.master.getvar('image_name_var')
    image_description = ctx.master.getvar('description_var')
    container_var = ctx.master.getvar('container_var')

    if not isinstance(image_name, int):
        try:
            image_number = int(image_number)
        except:
            return

    products = []
    sampling_dict = defaultdict(list)

    for trait, values in attribute_dict.items():
        _, weights, _ = list(zip(*values))
        sampling_dict[trait] = random.choices(values, weights=weights, k=image_number)

    for i in range(image_number):
        temp = {trait: values[i] for trait, values in sampling_dict.items()}
        products.append(Product(**temp))

    print('before: ', len(products))
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
            base_metadata['description'] = image_description
            base_metadata['attributes'].append(
                {'trait_type': trait_type, 'trait_value': part.trait_value}
            )
        base_tkimg = ImageTk.PhotoImage(base_img)
        _canvas = ctx.master.children['product_canvas']
        _canvas.itemconfigure(container_var, image=base_tkimg)

        # Save image.png and metadata.json
        base_img.save(f'{restore_path}/{i}.png')
        with open(f'{restore_path}/{i}.json', mode='w', encoding='utf-8') as f:
            json.dump(base_metadata, f)

        # todo
        ## base_tkimg 만들기


if __name__ == '__main__':
    root = tk.Tk()
    root.title('PFP Maker')
    root.geometry('380x720+100+100')

    style = ttk.Style(root)
    # windows : ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    # osx :
    os_name = platform.system()  # Windows, Darwin, Linux
    if os_name[0] == 'W':
        style.theme_use('vista')
    else:
        style.theme_use('aqua')  # Darwin, Linux

    # Frame Option
    # flat, groove, raised, ridge, solid, or sunken
    btn_style = {
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

    grid_opt = {
        'padx': 10,
        'pady': 10,
    }

    # Left Frame
    make_left_frame = ttk.Frame(make_frame, name='left_frame')
    make_left_frame.pack(side=tk.LEFT, fill='y')

    # Right Frame
    right_frame = ttk.Frame(make_frame, name='right_frame')
    right_frame.pack(side=tk.LEFT, fill='y')

    # Canvas Widget
    product_canvas = tk.Canvas(make_left_frame, width=300, height=300, name='product_canvas')
    img_container = product_canvas.create_image(300, 300)
    container_var = tk.IntVar(name='container_var', value=img_container)
    product_canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Asset button
    btn_load = ttk.Button(make_left_frame, name='btn_load', text="LOAD ASSET")
    btn_load['command'] = partial(on_load, btn_load)
    btn_load.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    # Image slider
    image_slider_var = tk.IntVar(make_left_frame, name='image_slider_var', value=0)
    image_slider = ttk.Scale(make_left_frame, name='image_slider', from_=0, to=0, variable=image_slider_var,
                             orient=tk.HORIZONTAL)

    image_slider.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    # name entry
    image_name_var = tk.StringVar(master=make_left_frame, name='image_name_var')
    image_name_entry = EntryWithPlaceholder(make_left_frame, placeholder='Image name', justify=tk.LEFT,
                                            textvariable=image_name_var, font=('System', 18))
    image_name_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    # Make description scrolled Text
    description_var = tk.StringVar(master=make_left_frame, name='description_var')
    description_text = ScrolledTextWithPlaceholder(
        make_left_frame,
        placeholder='description',
        name='description_text',
        height=4,
        width=26,
        font=('System', 18),
        highlightcolor='skyblue',
        highlightthickness=2
    )
    description_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # number entry
    image_num_var = tk.IntVar(master=make_left_frame, name='image_num_var')
    image_num_entry = EntryWithPlaceholder(make_left_frame, placeholder='Number', width=12, justify=tk.CENTER,
                                           textvariable=image_num_var,
                                           font=('System', 18))
    image_num_entry.grid(row=5, column=0, padx=10, pady=10, sticky='w')

    # Make Button
    btn_make = ttk.Button(make_left_frame, name='btn_shuffle', text='SUFFLE', state=tk.DISABLED)
    btn_make['command'] = partial(on_make, btn_make)
    btn_make.grid(row=5, column=1, padx=10, pady=10, sticky='e')

    # analysis_canvas
    analysis_canvas = tk.Canvas(analysis_frame, name='analysis_canvas', width=500, height=500)
    analysis_canvas.pack(side=tk.LEFT)

    # App run
    root.mainloop()
