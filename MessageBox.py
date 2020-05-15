from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox

root = Tk()
root.title("MessageBox")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')

#showinfo, showwarning, showerror, askquestion, askokcancel, askyesno
def popUp():
    # messagebox.showinfo("This is my first popup", "Hellow World")
    # messagebox.showwarning("This is my first popup", "Hellow World")
    # messagebox.showerror("This is my first popup", "Hellow World")
    # messagebox.askquestion("This is my first popup", "Hellow World")
    # messagebox.askokcancel("This is my first popup", "Hellow World")

    #Pot accesa valoarea din raspuns la askyesno / askokcancel / showerror returneaza ok / askquestion "yes"/"no
    # showwarning returneaza "ok", showinfo: "ok"
    response = messagebox.askyesno("This is my first popup", "Hellow World")
    if response == 1:
        Label(root, text="you clicked yes").pack()
    else:
        Label(root, text="You clicked no").pack()



mybtn = Button(root, text="Popup", command=popUp).pack()

root.mainloop()

