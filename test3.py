import tkinter as tk
from tkinter import ttk
import pandas as pd
from pandastable import Table


df = pd.DataFrame(data={
    'A': [10, 20, 10, 50, 35],
    'B': [5, 7, 1, 8, 2],
    'C': [100, 120, 95, 105, 105]
}, columns=['A', 'B', 'C'])

df.describe()

root = tk.Tk()
root.geometry('500x500+100+100')

frame = ttk.Frame(root)
frame.pack()

pt = Table(frame, dataframe=df, showtoolbar=False, showstatusbar=False)
pt.show()
# canvas = tk.Canvas(frame, width=400, height=400, bg='white')
# canvas.pack(pady=50)


root.mainloop()