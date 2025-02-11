import tkinter as tk
import random

window = tk.Tk()
window.geometry("250x200")

def roll():
    lbl_value["text"] = str(random.randint(1, 6))
  
window.rowconfigure([0, 1], minsize=50, weight=1)
window.columnconfigure(0, minsize=50, weight=1)

btn_roll = tk.Button(master=window, text="Roll", width=25, font=('arial', 20, 'bold'), command=roll)
btn_roll.grid(row=0, column=0, sticky="ns")

lbl_value = tk.Label(master=window, text="0", font=('arial', 40), width=25, bg='black', fg='white')
lbl_value.grid(row=1, column=0, sticky='nw')

window.mainloop()
