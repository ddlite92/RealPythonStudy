import tkinter as tk

window = tk.Tk()
window.title("Address Entry Form")
window.geometry("800x450")
window.configure(bg='black')
window.columnconfigure(0, minsize=50)
window.rowconfigure([0, 1, 2, 3, 5, 5, 6, 7, 8], minsize=50)

label1 = tk.Label(bg="black", fg="white", text="First Name:")
label1.grid(row=0, column=0, sticky="w")

label2 = tk.Label(bg="black", fg="white", text="Last Name:")
label2.grid(row=1, column=0, sticky="w")

label3 = tk.Label(bg="black", fg="white", text="Address Line 1:")
label3.grid(row=2, column=0, sticky="w")

label4 = tk.Label(bg="black", fg="white", text="Address Line 2:")
label4.grid(row=3, column=0, sticky="w")

label5 = tk.Label(bg="black", fg="white", text="Last Name:")
label5.grid(row=4, column=0, sticky="w")

label6 = tk.Label(bg="black", fg="white", text="City:")
label6.grid(row=5, column=0, sticky="w")

label7 = tk.Label(bg="black", fg="white", text="State/Province:")
label7.grid(row=6, column=0, sticky="w")

label8 = tk.Label(bg="black", fg="white", text="Postal Code:")
label8.grid(row=7, column=0, sticky="w")

label9 = tk.Label(bg="black", fg="white", text="Country")
label9.grid(row=8, column=0, sticky="w")

entry1 = tk.Entry(fg="black", bg="white", width=80)
entry1.grid(row=0, column=1, sticky="w")

entry2 = tk.Entry(fg="black", bg="white", width=80)
entry2.grid(row=1, column=1, sticky="w")

entry3 = tk.Entry(fg="black", bg="white", width=80)
entry3.grid(row=2, column=1, sticky="w")

entry4 = tk.Entry(fg="black", bg="white", width=80)
entry4.grid(row=3, column=1, sticky="w")

entry5 = tk.Entry(fg="black", bg="white", width=80)
entry5.grid(row=4, column=1, sticky="w")

entry6 = tk.Entry(fg="black", bg="white", width=80)
entry6.grid(row=5, column=1, sticky="w")

entry7 = tk.Entry(fg="black", bg="white", width=80)
entry7.grid(row=6, column=1, sticky="w")

entry8 = tk.Entry(fg="black", bg="white", width=80)
entry8.grid(row=7, column=1, sticky="w")

entry9 = tk.Entry(fg="black", bg="white", width=80)
entry9.grid(row=8, column=1, sticky="w")


#entry.pack()
#label1.pack()


window.mainloop()