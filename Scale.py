from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog

root = Tk()
root.title("Sliders")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("400x400")
vertical = Scale(root, from_= 0, to=200)
vertical.pack()

horizontal = Scale(root, from_=0, to=400, orient=HORIZONTAL)
horizontal.pack()


def slide():
    labelh = Label(root, text=horizontal.get()).pack()
    root.geometry(str(horizontal.get())+"x"+str(vertical.get()))



my_btn = Button(root, text="click", command=slide).pack()
root.mainloop()

