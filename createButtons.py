from tkinter import *

root = Tk()

def myClick():
    myLabel = Label(root, text="Look! I clicked a button")
    myLabel.grid(row=1, column=0)

def main():

    myButton = Button(root, text="Click me", command=myClick, fg="blue", bg="red")
    myButton.grid(row=0, column=0)



    root.mainloop()







if __name__ == "__main__":
    main()
