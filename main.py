import glob
import os, sys, platform

if getattr(sys, 'frozen', False):
    _path = sys.executable
else:
    _path = __file__

os.chdir(os.path.dirname(os.path.abspath(_path)))
import re, json, random
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from collections import defaultdict, namedtuple
from datetime import datetime
from functools import partial
from util import *
from widget import EntryWithPlaceholder, ScrolledTextWithPlaceholder
import pandas as pd
from pandastable import Table


img_list = []
Product = None
Part = namedtuple('Part', ('trait_value', 'weight', 'path'))

PATH_PREFIX = './traits'
RESTORE_PREFIX = './assets'
file_dict = None
attribute_dict = defaultdict(list)


def on_choose(ctx):
    asset_path = filedialog.askdirectory(initialdir=RESTORE_PREFIX)
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
            temp[attr_obj['trait_type']] = attr_obj['value']

        data.append(temp)

    df = pd.DataFrame(data=data)

    frame = ctx.master.nametowidget('.analysis_frame.table_frame')
    if '!table' not in frame.keys():
        pt = Table(frame, dataframe=df, width=frame.winfo_width(), showstatusbar=True, enable_menus=True, editable=True)
        pt.show()
    else:
        pt = frame.nametowidget('.analysis_frame.table_frame.!table')

    pt.redraw()



def on_slide(ctx, pos):
    global img_list
    try:
        pos = round(float(pos))
    except Exception as e:
        return

    container_var = ctx.master.getvar('container_var')
    _canvas = ctx.master.nametowidget('.make_frame.left_frame.product_canvas')
    _canvas.itemconfig(container_var, image=img_list[pos])


def on_select(event):
    w = event.widget
    selected_index = w.curselection()[0]


def on_load(ctx):
    ctx['state'] = tk.DISABLED
    ctx['text'] = 'LOADED'

    ctx.master.children['shuffle_label_frame'].children['btn_shuffle']['state'] = tk.NORMAL
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
    image_symbol = ctx.master.getvar('image_symbol_var')
    image_description = ctx.master.getvar('description_var')
    container = ctx.master.getvar('container_var')

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

    products = list(set(products))
    ## products는 완성품 배열

    sample_path = products[0][0].path
    sample_img = Image.open(sample_path)

    # Set restore path
    restore_path = f'{RESTORE_PREFIX}/{datetime.utcnow().strftime("%Y-%m-%d_%H%M%SZ")}'
    if not os.path.exists(restore_path):
        os.makedirs(restore_path)

    # Load metadata.json template
    with open('./base_metadata.json', mode='r') as f:
        metadata_template = json.load(f)

    # Set slider, canvas
    _left_frame = ctx.master.master.nametowidget('.make_frame.left_frame')
    _canvas = _left_frame.children['product_canvas']
    _slider = _left_frame.children['image_slider']
    _slider['to'] = len(products)-1
    if _slider['to'] < 0:
        _slider['to'] = 0
    _slider['state'] = tk.NORMAL

    global img_list
    for i, prod in enumerate(products):
        base_metadata = metadata_template.copy()
        base_img = Image.new(size=sample_img.size, mode='RGBA')

        base_metadata['attributes'] = []
        for trait_type, part in prod._asdict().items():
            part_img = Image.open(part.path, mode='r')
            base_img = Image.alpha_composite(base_img, part_img)
            base_metadata['name'] = f'{image_name} #{i+1}'
            base_metadata['symbol'] = image_symbol
            base_metadata['image'] = f"{i}.png"
            base_metadata['description'] = image_description
            base_metadata['properties']['files'][0]['uri'] = f'{i}.png'
            base_metadata['attributes'].append(
                {'trait_type': trait_type, 'value': part.trait_value}
            )

        base_tkimg = ImageTk.PhotoImage(base_img.resize(size=(int(_canvas['width'])-20, int(_canvas['height'])-20)))
        img_list.append(base_tkimg)
        _canvas.itemconfig(container, image=img_list[-1])

        # Save image.png and metadata.json
        base_img.save(f'{restore_path}/{i}.png')
        with open(f'{restore_path}/{i}.json', mode='w', encoding='utf-8') as f:
            json.dump(base_metadata, f)

    msg = '{:d} created uniquely'.format(len(products))
    result_var.set(msg)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('PFP Maker')
    root.configure(bg=Color.white)
    root.geometry('820x540+100+100')
    root.resizable(True, True)

    style = ttk.Style(root)
    # windows : ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    # osx : ('aqua', 'clam', 'alt', 'default', 'classic')
    os_name = platform.system()  # Windows, Darwin, Linux
    if os_name[0] == 'W':
        style.theme_use('vista')
    else:
        style.theme_use('aqua')  # Darwin, Linux

    # Frame Option
    frame_opt = {
        'padx': 10,
        'pady': 5,
    }
    # flat, groove, raised, ridge, solid, or sunken

    # Make notebook
    notebook = ttk.Notebook(root, name='notebook', width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    notebook.pack()

    # Make Frame
    make_frame = tk.Frame(root, name='make_frame')
    # make_frame.config(background=Color.WHITE)
    notebook.add(make_frame, text='MAKE')

    # Analysis Frame
    analysis_frame = tk.Frame(root, name='analysis_frame')
    notebook.add(analysis_frame, text='ANALYSIS')

    # Left Frame
    make_left_frame = tk.Frame(make_frame, name='left_frame')
    make_left_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Right Frame
    right_frame = ttk.Frame(make_frame, name='right_frame')
    right_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Canvas Widget
    product_canvas = tk.Canvas(make_left_frame, width=420, height=420, name='product_canvas')
    empty_img = Image.new(mode='RGBA', size=(400, 400))
    empty_tkimg = ImageTk.PhotoImage(empty_img)
    w, h = int(product_canvas['width']), int(product_canvas['height'])
    img_container = product_canvas.create_image(w//2, h//2, image=empty_tkimg)
    container_var = tk.IntVar(name='container_var', value=img_container)
    product_canvas.pack(padx=10, pady=5, fill=tk.BOTH)

    # Image slider
    image_slider_var = tk.IntVar(make_left_frame, name='image_slider_var', value=0)
    # sliderrelief : flat, groove, raised, ridge, solid, or sunken
    # relief = : flat, groove, raised, ridge, solid, or sunken
    image_slider = ttk.Scale(make_left_frame, name='image_slider', from_=0, to=0, variable=image_slider_var,
                             orient=tk.HORIZONTAL, state=tk.DISABLED)
    image_slider['command'] = partial(on_slide, image_slider)
    image_slider.pack(padx=10, pady=5, fill='x')

    # Asset button
    btn_load = ttk.Button(right_frame, name='btn_load', text="LOAD TRAIT")
    btn_load['command'] = partial(on_load, btn_load)
    btn_load.pack(fill=tk.X, **frame_opt)

    # name entry
    image_name_var = tk.StringVar(master=right_frame, name='image_name_var')
    image_name_entry = EntryWithPlaceholder(right_frame, placeholder='Image name', justify=tk.LEFT,
                                            textvariable=image_name_var, font=('System', 18))
    image_name_entry.pack(fill=tk.X, **frame_opt)

    # symbol entry
    image_symbol_var = tk.StringVar(master=right_frame, name='image_symbol_var')
    image_symbol_entry = EntryWithPlaceholder(right_frame, placeholder='symbol', justify=tk.LEFT,
                                              textvariable=image_symbol_var, font=('System', 18))
    image_symbol_entry.pack(fill=tk.X, **frame_opt)

    # collection entry
    image_collection_var = tk.StringVar(master=right_frame, name='image_collection_var')
    image_collection_entry = EntryWithPlaceholder(right_frame, placeholder='collection family', justify=tk.LEFT,
                                              textvariable=image_collection_var, font=('System', 18))
    image_collection_entry.pack(fill=tk.X, **frame_opt)

    # Make description scrolled Text
    description_var = tk.StringVar(master=right_frame, name='description_var')
    description_text = ScrolledTextWithPlaceholder(
        right_frame,
        placeholder='description',
        name='description_text',
        height=4,
        width=26,
        font=('System', 18),
        highlightcolor='skyblue',
        highlightthickness=2
    )
    description_text.pack(fill=tk.X, **frame_opt)

    # Suffle Label frame
    suffle_label_frame = ttk.Labelframe(right_frame, name='shuffle_label_frame', text='Number of Shuffling', height=100)
    suffle_label_frame.pack(fill=tk.BOTH, **frame_opt)

    # Number entry
    image_num_var = tk.IntVar(master=suffle_label_frame, name='image_num_var')
    image_num_entry = EntryWithPlaceholder(suffle_label_frame, placeholder='number', width=7, justify=tk.CENTER,
                                           textvariable=image_num_var,
                                           font=('System', 18))
    image_num_entry.place(width=130, anchor=tk.NW)

    # Suffle Button
    btn_shuffle = ttk.Button(master=suffle_label_frame, name='btn_shuffle', text='SUFFLE', state=tk.DISABLED)
    btn_shuffle['command'] = partial(on_make, btn_shuffle)
    btn_shuffle.place(anchor=tk.NW, x=150, width=130)

    # Result label
    result_var = tk.StringVar(master=suffle_label_frame, name='result_var', value='')
    result_label = ttk.Label(master=suffle_label_frame, name='result_label', textvariable=result_var)
    result_label.place(relx=0.3, y=45)

    # Choose Button
    btn_choose = ttk.Button(analysis_frame, text='CHOOSE ASSET')
    btn_choose['command'] = partial(on_choose, btn_choose)
    btn_choose.pack(fill='x', **frame_opt)

    # Table frame
    table_frame = ttk.Frame(analysis_frame, name='table_frame')
    table_frame.pack(fill=tk.BOTH, expand=True)

    # App run
    root.mainloop()
