# Profile Picture Maker

For NFT project.


## Quick start
```bash
python main.py
```

## Install
```bash
git clone ...

cd pfp-maker

python -m venv venv

pip install -r -requirements.txt
```

## Usage
* PFP resources are in `./traits` named `<trait order>_<trait type>/`


```bash
pfp-maker/
├── README.md
├── assets/
├── main.py
├── metadata.json  # metadata template
├── requirements.txt
├── test.py
├── test2.py
├── test3.py
├── traits
│   ├── 0_head
│   │   ├── head_circle_black.png
│   │   ├── head_circle_blue.png
│   │   ├── head_circle_pink.png
│   │   ├── head_circle_red.png
│   │   ├── head_square_black.png
│   │   ├── head_square_blue.png
│   │   ├── head_square_pink.png
│   │   ├── head_square_red.png
│   │   ├── head_triangle_black.png
│   │   ├── head_triangle_blue.png
│   │   ├── head_triangle_pink.png
│   │   └── head_triangle_red_5000.png
│   ├── 1_eyes
│   │   ├── eyes_angry_cyan.png
│   │   ├── eyes_angry_pink.png
│   │   ├── eyes_angry_yellow.png
│   │   ├── eyes_pretty_cyan.png
│   │   ├── eyes_pretty_pink.png
│   │   └── eyes_pretty_yellow.png
│   └── 2_mouth
│       ├── mouth_open_goldtooth.png
│       ├── mouth_open_smile.png
│       └── mouth_open_white.png
└── venv/

```

2. In `<order>_<trait type>` directory, `<trait value>.png` must be same size with the `*.png`
3. Click LOAD ASSETS button.
4. Click MAKE IMAGES button.

