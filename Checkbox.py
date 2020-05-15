from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog

root = Tk()
root.title("Checkbox")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("500x500")

def showSelection():
    myLabel = Label(root, text=var.get()).pack()


#Pot sa pun pe checked si unchecked tot ce vreau eu ca valori
var = StringVar()
c = Checkbutton(root, text="Check this box", variable=var, onvalue="pizza", offvalue="Smac")
c.deselect()
c.pack()


myButton = Button(root, text="Show selection", command=showSelection).pack()


root.mainloop()

