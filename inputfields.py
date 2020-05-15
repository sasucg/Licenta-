from tkinter import *

root = Tk()
# Pot pune bg, fg pe Entry(input)
e = Entry(root, width=50)
e.pack()
e.insert(0, "Enter your name: ")
def myClick():

    hello = "Hellow " + e.get()
    myLabel = Label(root, text = hello )
    myLabel.pack()



myButton = Button(root, text="Enter your name", command=myClick).pack()










root.mainloop()

