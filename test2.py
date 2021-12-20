import tkinter as tk
from tkinter import ttk
from functools import partial
import pandas


def on_analysis(_frame):
    _canvas = _frame.nametowidget('.frame.canvas')
    print(_canvas)
    _canvas.item


if __name__ == '__main__':
    root = tk.Tk(baseName='My PFP', screenName='hello', className='Profile Picture Maker')
    root.geometry('1280x720+100+100')

    style = ttk.Style(root)
    style.theme_use('aqua')

    frame = ttk.Frame(root, name='frame')
    frame.grid()

    canvas = tk.Canvas(frame, name='canvas', width=500, height=500)
    canvas.grid()

    btn = ttk.Button(frame, text='Analysis', name='btn', command=partial(on_analysis, frame))
    btn.grid()

    treeview = ttk.Treeview(frame, columns=['1', '2', '3'], displaycolumns=['1', '2', '3'])
    treeview.grid(row=0, column=1)
    treeview.column('#0', width=0, stretch=tk.OFF)
    treeview.column('1', anchor=tk.CENTER)
    treeview.column('2', anchor=tk.CENTER)
    treeview.column('3', anchor=tk.CENTER)
    treeview.heading('#0', text='index', anchor=tk.W)
    treeview.heading('1', text='head', anchor=tk.W)
    treeview.heading('2', text='number', anchor=tk.W)
    treeview.heading('3', text='leg', anchor=tk.W)

    treeview.insert('', tk.END, values=('big', '10', 'long'))


    # canvas.delete(tid)
    # for e in dir(canvas):
    #     print(e)

    root.mainloop()