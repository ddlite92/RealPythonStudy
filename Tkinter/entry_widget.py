import tkinter as tk

window = tk.Tk()


entry = tk.Entry(fg="black", bg="white", width=40)
entry.pack()
entry.insert(0, "What is your name? ")


window.mainloop()