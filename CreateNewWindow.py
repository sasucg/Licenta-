from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox

root = Tk()
root.title("Create new window")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')

def open():
    # Creez, schimb titlu si iconita la fereastra noua
    top = Toplevel()
    top.title("Imaginea mea")
    top.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')

    #Foarte important sa pun global ca sa apara imaginea
    global my_img
    my_img = ImageTk.PhotoImage(Image.open("images/img2.jpg"))
    my_label = Label(top, image=my_img).pack()

    btn2 = Button(top, text="close", command=top.destroy).pack()


btn = Button(root, text="Open second window", command=open).pack()







root.mainloop()

