from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import sqlite3

root = Tk()
root.title("Create new window")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("500x500")

#Using Databases

#Create a database or connect to one
conn = sqlite3.connect('address_book.db')

#Create a cursor
cursor = conn.cursor()


#Create table
cursor.execute("""CREATE TABLE addresses (
        first_name text,
        last_name text,
        adress text,
        city text,
        state text,
        zipcode integer
        )""")


#Commit changes
conn.commit()

#Close connection
conn.close()

root.mainloop()

