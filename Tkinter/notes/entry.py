#!/usr/bin/env python3

import tkinter as tk

window = tk.Tk()

label = tk.Label(text="Name")
entry = tk.Entry()
name = entry.get()
entry.delete(0)

label.pack()
entry.pack()

window.mainloop()