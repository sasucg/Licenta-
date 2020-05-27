from tkinter import *

root = Tk()
my_name_is = Label(root, text="Eu mă numesc: ")
my_name_is.grid(row=0, column=0)
e = Entry(root, width=50)
e.grid(row=0, column=1)

def myClick():
    myLabel = Label(root, text = "Salutare, " + e.get() + "! Ce faci?" )
    myLabel.grid(row=2, column=0, columnspan=2)

myButton = Button(root, text="Click!", command=myClick)
myButton.grid(row=1, column=0, columnspan=2)

root.mainloop()

