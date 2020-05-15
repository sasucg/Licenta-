from tkinter import *
from PIL import ImageTk, Image
root = Tk()
root.title("Icons and Images")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')

def forward(image_number):
    global my_label
    global button_forward
    global button_back

    my_label.grid_forget()
    my_label = Label(root, image=image_List[image_number-1])
    my_label.grid(row=0, column=0, columnspan=3)
    button_forward = Button(root, text=">>", width = 30, command=lambda: forward(image_number+1)).grid(row=1, column=2)
    button_back = Button(root, text="<<", width = 30, command=lambda: back(image_number - 1)).grid(row=1, column=0)

    if image_number == 4:
        button_forward = Button(root, text=">>", state=DISABLED).grid(row=1, column=2)

    status = Label(root, text="Image " + str(image_number) + " of " + str(len(image_List)), bd=1, relief=SUNKEN, anchor=E)
    status.grid(row=2, column=0, columnspan=3, sticky=W + E)

def back(image_number):
    global my_label
    global button_forward
    global button_back

    my_label.grid_forget()
    my_label = Label(root, image=image_List[image_number - 1])
    my_label.grid(row=0, column=0, columnspan=3)
    button_forward = Button(root, text=">>", width = 30,  command=lambda: forward(image_number + 1)).grid(row=1, column=2)
    button_back = Button(root, text="<<", width = 30,  command=lambda: back(image_number - 1)).grid(row=1, column=0)

    if image_number == 1:
        button_back = Button(root, text="<<", state=DISABLED).grid(row=1, column = 0)

    status = Label(root, text="Image " + str(image_number) + " of " + str(len(image_List)), bd=1, relief=SUNKEN, anchor=E)
    status.grid(row=2, column=0, columnspan=3, sticky=W + E)


my_img0 = ImageTk.PhotoImage(Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/img0.jpg"))
my_img1 = ImageTk.PhotoImage(Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/img1.jpg"))
my_img2 = ImageTk.PhotoImage(Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/img2.jpg"))
my_img3 = ImageTk.PhotoImage(Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/img3.jpg"))

my_label = Label(root, image=my_img0)
my_label.grid(row=0, column=0, columnspan=3)

image_List = [my_img0, my_img1, my_img2, my_img3 ]


status = Label(root, text="Image " +" of " + str(len(image_List)), bd=1, relief=SUNKEN, anchor=E)
status.grid(row=2, column=0, columnspan=3, sticky=W+E)
button_back = Button(root, text="<<", width = 30, command=lambda: back(0), state=DISABLED).grid(row=1, column = 0)
button_quit = Button(root, text="Exit", width = 30, command=root.quit).grid(row=1, column = 1, pady=10)
button_next = Button(root, text=">>", width = 30, command=lambda: forward(2)).grid(row=1, column = 2)

root.mainloop()

