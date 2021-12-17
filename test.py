import tkinter as tk
from tkinter import ttk
import pandas
from tkinter import filedialog


if __name__ == '__main__':
    root = tk.Tk(baseName='My PFP', screenName='hello', className='Profile Picture Maker')
    root.geometry('1280x720+100+100')

    style = ttk.Style(root)
    style.theme_use('aqua')

    canvas = tk.Canvas(root, width=500, height=500, bg='black')
    canvas.pack()

    root.directory = filedialog.askdirectory(initialdir='./')

    print(root.directory)
    root.mainloop()