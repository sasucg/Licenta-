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


#Create table Dupa ce am rulat o data o pot comenta pentru ca nu mai e nevoie sa o creez iar
cursor.execute("""CREATE TABLE addresses (
        first_name text,
        last_name text,
        adress text,
        city text,
        state text,
        zipcode integer
        )""")


#Commit changes

#Create submitfunction for database
def submit():
    # Create a database or connect to one
    conn = sqlite3.connect('address_book.db')
    # Create a cursor
    cursor = conn.cursor()

    #Insert into table
    cursor.execute("INSERT INTO addresses VALUES (:f_name, :l_name, :adress, :city, :state, :zipcode)",
              {
                  'f_name': f_name.get(),
                  'l_name': l_name.get(),
                  'adress': adress.get(),
                  'city': city.get(),
                  'state': state.get(),
                  'zipcode': zipcode.get(),
              })

    #Clear the textboxes
    f_name.delete(0, END)
    l_name.delete(0, END)
    adress.delete(0, END)
    city.delete(0, END)
    state.delete(0, END)
    zipcode.delete(0, END)

    conn.commit()
    # Close connection
    conn.close()


# Create function to delete a record
def delete():
    # Create a database or connect to one
    conn = sqlite3.connect('address_book.db')
    # Create a cursor
    cursor = conn.cursor()

    #Delete a record
    cursor.execute("DELETE from addresses where oid="+select_box.get())


    conn.commit()
    # Close connection
    conn.close()

#Create a update function to save records to database
def update(updated):
    # Create a database or connect to one
    conn = sqlite3.connect('address_book.db')
    # Create a cursor
    cursor = conn.cursor()

    record_id = select_box.get()
    cursor.execute("""UPDATE addresses SET
            first_name = :first,
            last_name = :last,
            adress = :address,
            city = :city,
            state = :state,
            zipcode = :zipcode
    
            where oid = :oid""",
       {'first': f_name_editor.get(),
        'last': l_name_editor.get(),
        'address': adress_editor.get(),
        'city': city_editor.get(),
        'state': state_editor.get(),
        'zipcode': zipcode_editor.get(),
        'oid': record_id
       })
    conn.commit()
    # Close connection
    conn.close()
    editor.destroy()



# creade a edit function to update a record
# creade a edit function to update a recor
def edit():
    global editor
    editor = Tk()
    editor.title("Edit a record")
    editor.geometry("400x400")

    # Create a database or connect to one
    conn = sqlite3.connect('address_book.db')
    # Create a cursor
    cursor = conn.cursor()



    # Query the database
    cursor.execute("SELECT * from addresses where oid="+select_box.get())
    # .fetchone / .fetchmany(50)
    records = cursor.fetchall()

    # Create global variables for text  box names
    global f_name_editor
    global l_name_editor
    global adress_editor
    global city_editor
    global state_editor
    global zipcode_editor

    # Create text boxes
    f_name_editor = Entry(editor, width=30)
    f_name_editor.grid(row=0, column=1, padx=20, pady=(10, 0))
    l_name_editor = Entry(editor, width=30)
    l_name_editor.grid(row=1, column=1)
    adress_editor = Entry(editor, width=30)
    adress_editor.grid(row=2, column=1)
    city_editor = Entry(editor, width=30)
    city_editor.grid(row=3, column=1)
    state_editor = Entry(editor, width=30)
    state_editor.grid(row=4, column=1)
    zipcode_editor = Entry(editor, width=30)
    zipcode_editor.grid(row=5, column=1)

    # loop thru results
    for record in records:
        f_name_editor.insert(0, record[0])
        l_name_editor.insert(0, record[1])
        adress_editor.insert(0, record[2])
        city_editor.insert(0, record[3])
        state_editor.insert(0, record[4])
        zipcode_editor.insert(0, record[5])


    # Create textbox labels
    f_name_label = Label(editor, text="First Name")
    f_name_label.grid(row=0, column=0, pady=(10, 0))
    l_name_label = Label(editor, text="Last Name")
    l_name_label.grid(row=1, column=0)
    adress_label = Label(editor, text="Adress")
    adress_label.grid(row=2, column=0)
    city_label = Label(editor, text="City")
    city_label.grid(row=3, column=0)
    state_label = Label(editor, text="State")
    state_label.grid(row=4, column=0)
    zipcode_label = Label(editor, text="Zipcode")
    zipcode_label.grid(row=5, column=0)

    save_button_editor = Button(editor, text="Save", command=lambda: update(select_box.get()))
    save_button_editor.grid(row=6, column=0, columnspan=2, padx=10, pady=10, ipadx=140)

    conn.commit()
    # Close connection
    conn.close()



#Create a query function
def querry():
    # Create a database or connect to one
    conn = sqlite3.connect('address_book.db')
    # Create a cursor
    cursor = conn.cursor()

    #Query the database
    cursor.execute("SELECT *, oid from addresses")
    #.fetchone / .fetchmany(50)
    records = cursor.fetchall()
    #print(records)

    #loop thru results
    print_records = ''
    for record in records:
        print_records += str(record[0]) + " " + " \t " + str(record[6]) + '\n'

    query_label = Label(root, text=print_records)
    query_label.grid(row=12, column=0, columnspan=2, ipady=10)




    conn.commit()
    # Close connection
    conn.close()


#Create text boxes
f_name = Entry(root, width=30)
f_name.grid(row=0, column=1, padx=20, pady=(10, 0))
l_name = Entry(root, width=30)
l_name.grid(row=1, column=1)
adress = Entry(root, width=30)
adress.grid(row=2, column=1)
city = Entry(root, width=30)
city.grid(row=3, column=1)
state = Entry(root, width=30)
state.grid(row=4, column=1)
zipcode = Entry(root, width=30)
zipcode.grid(row=5, column=1)

select_box = Entry(root, width=30)
select_box.grid(row=8, column=1)

#Create textbox labels
f_name_label = Label(root, text="First Name")
f_name_label.grid(row=0, column=0, pady=(10, 0))
l_name_label = Label(root, text="Last Name")
l_name_label.grid(row=1, column=0)
adress_label = Label(root, text="Adress")
adress_label.grid(row=2, column=0)
city_label = Label(root, text="City")
city_label.grid(row=3, column=0)
state_label = Label(root, text="State")
state_label.grid(row=4, column=0)
zipcode_label = Label(root, text="Zipcode")
zipcode_label.grid(row=5, column=0)
select_box_label = Label(root, text="Select ID")
select_box_label.grid(row=8, column=0)


#Create submit button
submit_btn = Button(root, text="Add record to database", command=submit)
submit_btn.grid(row=6, column=0, columnspan=2, pady=10, padx=10, ipadx=100)

# Create a query bytton
querry_btn = Button(root, text="Show Records", command=querry)
querry_btn.grid(row=7, column=0, columnspan=2, pady=10, padx=10, ipadx=125)

#Create a delete button
delete_btn = Button(root, text="Delete Record", command=delete)
delete_btn.grid(row=10, column=0, columnspan=2, pady=10, padx=10, ipadx=126)

#Create a update button
update_btn = Button(root, text="Update Record", command=edit)
update_btn.grid(row=11, column=0, columnspan=2, pady=10, padx=10, ipadx=124)

conn.commit()
#Close connection
conn.close()

root.mainloop()

