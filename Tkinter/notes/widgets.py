#!/usr/bin/env python3

import tkinter as tk
from tkinter import *

window = tk.Tk()

greeting = tk.Label(
    text="Hello, Tkinter",
    fg='green',
    bg='black',
    width=20,
    height=5,
)

button = tk.Button(
    text="Click me!",
    width=20,
    height=5,
    bg="black",
    fg="yellow",
)

entry = tk.Entry(fg="white", bg="black", width=20)

button.pack()
greeting.pack()
entry.pack()



window.mainloop()