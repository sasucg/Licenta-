from tkinter import *

def main():
    root = Tk()

#Creating a label Widget
    myLabel1 = Label(root, text = "Hello World!123").grid(row = 0, column=0)
    myLabel2 = Label(root, text="My name is Sasu Catalin")
#Shoving it onto the screen
    # myLabel1.grid(row = 0, column=0)
    myLabel2.grid(row = 1, column=5)


    root.mainloop()










if __name__ == "__main__":
    main()
