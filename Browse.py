from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog

root = Tk()
root.title("Browse")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')

def open():
    global my_image
    #root.filename returneaza calea catre ceea ce selectez, initialdir e ce se deschide, filetypes e ce tipuri pot accepta si trebuie sa respecte patternul ("png files", "*.png")
    root.filename = filedialog.askopenfilename(initialdir="C:/Users/lenovo/PycharmProjects/LicentaSasu/images", title="Select a file", filetypes=(("png files", "*.png"),("jpeg files","*.jpg"),("all files","*.*")))
    my_image = ImageTk.PhotoImage(Image.open(root.filename))
    top = Toplevel()
    top.title("Imaginea mea")
    top.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
    my_image_label = Label(top, image=my_image).pack()

my_btn = Button(root, text="Browse", command=open).pack()

root.mainloop()

