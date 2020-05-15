from tkinter import *
from PIL import ImageTk, Image
root = Tk()
root.title("Frames and Radio Buttons")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')

frame = LabelFrame(root, text="This is my first frame", padx=5, pady=5) #padding inside frame
frame.pack() #padding outside frame


# r = IntVar()
# r.set("2")

#Creez lista de optiuni (text, value)
MODES = [
    ("Pepperoni", "Pepperoni"),
    ("Chesee", "Chesee"),
    ("Mushrooms", "Mushrooms"),
    ("Onion", "Onion"),
]

pizza = StringVar()
pizza.set("Pepperoni")

for text, mode in MODES:
    Radiobutton(frame, text=text, variable=pizza, value=mode).pack(anchor=W)

def clicked(value):
    myLabel = Label(frame, text=value)
    myLabel.pack()

def clicked2(value):
    myLabel = Label(frame, text=value)
    myLabel.pack()

#Radiobutton(root, text="Option 1", variable=r, value=1, command=lambda: clicked(r.get())).grid(row=0, column=1)
#Radiobutton(root, text="Option 2", variable=r, value=2, command=lambda: clicked(r.get())).grid(row=1, column=1)

myLabel = Label(frame, text=pizza.get())
myLabel.pack()

myButton = Button(text="Clickme",command=lambda: clicked2(pizza.get()))
myButton.pack()

root.mainloop()

