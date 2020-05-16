from tkinter import *
from datetime import date
import sqlite3
from tkinter import messagebox, ttk
import operator
import tkinter.font as tkFont
from PIL import ImageTk, Image
from tkinter import filedialog
import requests
import json

root = Tk()
root.title("Schedule App")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("1400x800")
root.resizable(False, False)

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Tabela a fost deja creata folosind aceste instructiuni
# cursor.execute("""CREATE TABLE users (
#         first_name text,
#         last_name text,
#         username text,
#         password text,
#         email text,
#         program text,
#         profile text,
#         specialization text,
#         schoolarship text,
#         year text
#         )""")
# #

def allFieldsCompleted():
    fields_ok = 1
    if first_name_register_input.get() == "" or last_name_register_input.get() == "" or username_register_input.get() == "" or password_register_input.get() == "" or email_register_input.get() == "":
        response = messagebox.showerror("Eroare!", "Nu ati completat toate campurile!")
        fields_ok = 0
    return fields_ok


def userExists():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * from users")
    users_database = cursor.fetchall()
    exists = "missing"
    for user_database in users_database:
        username_test = user_database[2]
        if username_test == username_register_input.get():
            break
    conn.commit()
    conn.close()
    return exists


def emailFormat():
    email_format = "unknownformat"
    if '@' in email_register_input.get() and '.' in email_register_input.get():
        email_format = "emailformat"
    return email_format


def register_database_function():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    first_name_register_label.config(fg="black")
    last_name_register_label.config(fg="black")
    username_register_label.config(fg="black")
    password_register_label.config(fg="black")
    email_register_label.config(fg="black")

    if allFieldsCompleted() == 0:
        if first_name_register_input.get() == "":
            first_name_register_label.config(fg="red")
        if last_name_register_input.get() == "":
            last_name_register_label.config(fg="red")
        if username_register_input.get() == "":
            username_register_label.config(fg="red")
        if password_register_input.get() == "":
            password_register_label.config(fg="red")
        if email_register_input.get() == "":
            email_register_label.config(fg="red")
    elif userExists() != "missing":
        reponse = messagebox.showerror("Error!", "Username deja folosit!")
    elif emailFormat() == "emailformat":
        cursor.execute("INSERT INTO users VALUES (:f_name, :l_name, :username, :password, :email, :program, :profile, :specialization, :school, :year)",
                       {
                           'f_name': first_name_register_input.get(),
                           'l_name': last_name_register_input.get(),
                           'username': username_register_input.get(),
                           'password': password_register_input.get(),
                           'email': email_register_input.get(),
                           'program': program_register_drop.get(),
                           'profile': profile_register_drop.get(),
                           'specialization': specialization_register_drop.get(),
                           'school': schoolship_register_drop.get(),
                           'year': year_register_drop.get()
                       })
        response = messagebox.showinfo("Info!", "Inregistrarea a avut loc cu succes! ")
        if response == "ok":
            reg.destroy()

    else:
        reponse = messagebox.showerror("Error!", "Emailul are formatul incorect!!")

    conn.commit()
    conn.close()


def login_function():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users_database = cursor.fetchall()

    logged_in = "fail"
    #Caut userul si parola in userii din baza de date
    for user_database in users_database:
        if user_database[2] == username_login_input.get() and user_database[3] == password_login_input.get():
            logged_in = "succes"
            break

    if logged_in == "fail":
        response = messagebox.showerror("Error", "Datele introduse sunt invalide! Reincercati!")
    else:
        login_frame.grid_forget()
        logged_in_function()


    conn.commit()
    conn.close()


def logout_function():
    response = messagebox.askyesno("Disconnect", "Doriti sa va delogati?")
    if response == True:
        logged_in_frame.destroy()
        login_frame_show()
        username_login_input.config(text="")
        password_login_input.config(text="")
    else:
        return


# Functia furnizeaza first name-ul si original id-ul userului logat
def querry_data_logged_user(logged_user):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    sql_query = """SELECT oid, first_name, year, specialization FROM users WHERE username = ?"""
    cursor.execute(sql_query, (logged_user,))
    user_database = cursor.fetchone()

    conn.commit()
    conn.close()

    return user_database[0], user_database[1], user_database[2], user_database[3]


#Functia furnizeaza semestrul actual
def get_current_semester():
    today = date.today()
    today_format = today.strftime("%m/%d/%y")
    today_month = str(today_format[0] + today_format[1])
    today_day = str(today_format[3] + today_format[4])

    current_semester = 0
    if int(today_month) >= 10 or int(today_month) < 2:
        current_semester = 1
    if int(today_month) > 2 and int(today_month) < 6:
        current_semester = 2
    if int(today_month) == 2:
        if int(today_day) < 15:
            current_semester = 1
        else:
            current_semester = 2

    return current_semester


# Functia cauta in baza de date materiile corespunzatoare: specializarii userului, anul si semestrul
def querry_courses(year, semester):
    conn = sqlite3.connect('materii.db')
    cursor = conn.cursor()

    sql_query = """SELECT nume FROM materii WHERE specializare = ? AND an = ? and semestru = ?"""
    cursor.execute(sql_query, (logged_specialization, year, semester))
    courses_database = cursor.fetchall()

    conn.commit()
    conn.close()
    return courses_database


# Functia apeleaza functia care furnizeaza materiile curente si le afiseaza
# TO BE DESIGNED000003
def querry_current_courses():
    courses_window = Toplevel()
    courses_window.title("Materii")
    courses_window.geometry("450x500")

    current_semester = get_current_semester()

    courses_database = querry_courses(logged_year, current_semester)

    if current_semester == 0:
        print("Vacanta de vara! Vacanta placuta")
    else:
        hi_courses = Label(courses_window, text="Materiile pentru care trebuie sa te pregatesti sunt cele din: /t Anul "+logged_year+", semestrul "+str(current_semester))
        hi_courses.pack()
        for course in courses_database:
            course_label = Label(courses_window, text=course[0])
            course_label.pack()


# Functia e folosita in querry_grades pentru putea itera prin ani si sa putem afisa notele din anii trecuti
def get_current_year_as_int():
    if logged_year == "III": return 3
    if logged_year == "II": return 2
    if logged_year == "I": return 1


# Functia e folosita in querry_grades pentru a ne permite sa apelan querry_courses dupa an(string) / semestru
def get_year_as_string(int_year):
    if int_year == 1: return "I"
    if int_year == 2: return "II"
    if int_year == 3: return "III"

# Functia furnizeaza notele obtinute la fiecare materie pana in prezent
def querry_grades():
    grades_window = Toplevel()
    grades_window.title("Carnet de note")
    grades_window.geometry("450x800")

    # gresit as fuck
    # current_semester = 1
    # print(current_semester)
    # current_year = get_current_year_as_int()
    # print(current_year)
    # int_post_year = 1
    # int_post_semester = 1
    # while int_post_year != current_year or int_post_semester != current_semester:
    #     print(int_post_year, int_post_semester)
    #     post_year = get_year_as_string(int_post_year)
    #     info_label = Label(grades_window, text="Anul "+str(post_year)+" semestrul "+str(int_post_semester))
    #     info_label.pack()
    #     courses = querry_courses(post_year, int_post_semester)
    #
    #     for course in courses:
    #         course_label_grades = Label(grades_window, text=course[0])
    #         course_label_grades.pack()
    #
    #     int_post_semester += 1
    #     if int_post_semester == 3:
    #         int_post_year += 1
    #         int_post_semester = 1
    #
    # if (int_post_year == 3 and int_post_semester == 2) or (int_post_year == 2 and int_post_semester == 2) or (int_post_year == 1 and int_post_semester == 2):
    #     print(int_post_year, int_post_semester)
    #     post_year = get_year_as_string(int_post_year)
    #     info_label = Label(grades_window, text="Anul " + str(post_year) + " semestrul " + str(int_post_semester))
    #     info_label.pack()
    #     courses = querry_courses(post_year, int_post_semester)
    #
    #     for course in courses:
    #         course_label_grades = Label(grades_window, text=course[0])
    #         course_label_grades.pack()


def logged_in_function():
    global logged_in_frame
    logged_in_frame = LabelFrame(root, bg="white",  width=1000, height=700, bd=0, padx=60, pady=30)
    logged_in_frame.place(relx=.15, rely=.1)
    logged_user = username_login_input.get()
    global logged_original_id
    global logged_name
    global logged_year
    global logged_specialization
    (logged_original_id, logged_name, logged_year, logged_specialization) = querry_data_logged_user(logged_user)


    #Pentru a manipula Welcome label text si logout button, schimb valorile din padx din gridurile lor
    top_bar_frame = LabelFrame(logged_in_frame, width=850, height=100, bg="white")
    top_bar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    welcome_label = Label(top_bar_frame, text="Salut, " + logged_name + "!", bg="white", font=("Helvetica", 15))
    welcome_label.grid(row=0, column=0, padx=(10,170))
    logout_button = Button(top_bar_frame, text="Log off", command=logout_function)
    logout_button.grid(row=0, column=1, sticky="ew", padx=(475, 0))

    menu_frame = LabelFrame(logged_in_frame, bg="white", width=850, height=500)
    menu_frame.grid(row=1, column=0)

    profile_button_menu = Button(menu_frame, text="Profil", pady=83, padx=110, bd=0)
    profile_button_menu.grid(row=0, column=0 , sticky="ew")
    courses_button_menu = Button(menu_frame, text="Materii", pady=83, padx=110, bd=0, command=querry_current_courses)
    courses_button_menu.grid(row=0, column=1, sticky="ew", padx=10)
    timetable_button_menu = Button(menu_frame, text="Orar", pady=83, padx=110, bd=0)
    timetable_button_menu.grid(row=0, column=2, sticky="ew")
    hobbies_button_menu = Button(menu_frame, text="Hobbies", pady=83, padx=110, bd=0)
    hobbies_button_menu.grid(row=1, column=0, sticky="ew", pady=10)
    schedule_button_menu = Button(menu_frame, text="Schedule", pady=83, padx=110, bd=0)
    schedule_button_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
    session_schedule_button_menu = Button(menu_frame, text="Schedule Sesiune", pady=83, padx=90, bd=0)
    session_schedule_button_menu.grid(row=1, column=2, sticky="ew", pady=10)
    carnet_button_menu = Button(menu_frame, text="Carnet", pady=83, padx=110, bd=0, command=querry_grades)
    carnet_button_menu.grid(row=2, column=0 , sticky="ew")
    calendar_button_menu = Button(menu_frame, text="Calendar", pady=83, padx=110, bd=0)
    calendar_button_menu.grid(row=2, column=1, sticky="ew", padx=10)
    faq_button_menu = Button(menu_frame, text="FAQ", pady=83, padx=110, bd=0)
    faq_button_menu.grid(row=2, column=2, sticky="ew")



# Nu vreau mai multe ferestre din register pe ecran TO BE DONE
def register_window_show():
    #Fereastra reg este globala pentru a putea fi distrusa in momentul in care un user s a inregistrat
    global reg
    reg = Toplevel()
    reg.title("Register")
    reg.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
    reg.geometry("450x800")
    frame_register = LabelFrame(reg, padx=20, pady=50)
    frame_register.grid(row=0, column=0, pady=50, padx=40)

    #Listele pentru Dropdowns
    study_programs = [
        "Licenta"
    ]
    study_profiles = [
        "Informatica",
        "Matematica",
        "CTI"
    ]
    study_specializations = [
        "Informatica",
        "CTI",
        "Matematica",
        "Mate-Info",
        "Mate-Aplicata"
    ]
    study_schoolarships = [
        "ID",
        "IF"
    ]
    study_years = [
        "I",
        "II",
        "III",
        "IV"
    ]

    # Label Texts pentru Register
    # Sunt globale pentru a le putea valida in registerDatabase (le schimb culoarea daca sunt necompletate)
    global first_name_register_label
    global last_name_register_label
    global username_register_label
    global password_register_label
    global email_register_label
    first_name_register_label = Label(frame_register, text="Prenume: ")
    first_name_register_label.grid(row=0, column=0, sticky=W)
    last_name_register_label = Label(frame_register, text="Nume: ")
    last_name_register_label.grid(row=1, column=0, sticky=W)
    username_register_label = Label(frame_register, text="Username: ")
    username_register_label.grid(row=2, column=0, sticky=W)
    password_register_label = Label(frame_register, text="Parola: ")
    password_register_label.grid(row=3, column=0, sticky=W)
    email_register_label = Label(frame_register, text="Email: ")
    email_register_label.grid(row=4, column=0, sticky=W)
    study_program_label = Label(frame_register, text="Programul de studiu: ")
    study_program_label.grid(row=5, column=0, pady=(20,0), sticky=W)
    profile_register_label = Label(frame_register, text="Profil: ")
    profile_register_label.grid(row=6, column=0, sticky=W, pady=(4,0))
    specialization_register_label = Label(frame_register, text="Specializare: ")
    specialization_register_label.grid(row=7, column=0, sticky=W, pady=(4,0))
    schoolship_register_label = Label(frame_register, text="Forma invatamant: ")
    schoolship_register_label.grid(row=8, column=0, sticky=W, pady=(4,0))
    year_register_label = Label(frame_register, text="Anul de studiu: ")
    year_register_label.grid(row=9, column=0, sticky=W, pady=(4,0))


    # Input fields pentru Register
    # Sunt globale pentru a putea fi accesate din functia registerDatabase()
    global first_name_register_input
    global last_name_register_input
    global username_register_input
    global password_register_input
    global email_register_input
    global program_register_drop
    global profile_register_drop
    global specialization_register_drop
    global schoolship_register_drop
    global year_register_drop
    first_name_register_input = Entry(frame_register, width=30)
    first_name_register_input.grid(row=0, column=1, padx=15)
    last_name_register_input = Entry(frame_register, width=30)
    last_name_register_input.grid(row=1, column=1)
    username_register_input = Entry(frame_register, width=30)
    username_register_input.grid(row=2, column=1)
    password_register_input = Entry(frame_register, width=30)
    password_register_input.grid(row=3, column=1)
    email_register_input = Entry(frame_register, width=30)
    email_register_input.grid(row=4, column=1)

    program_register_drop = ttk.Combobox(frame_register, value=study_programs)
    program_register_drop.grid(row=5, column=1, pady=(20,0))
    program_register_drop.current(0)
    profile_register_drop = ttk.Combobox(frame_register, value=study_profiles)
    profile_register_drop.grid(row=6, column=1, pady=(4,0))
    profile_register_drop.current(0)
    specialization_register_drop = ttk.Combobox(frame_register, value=study_specializations)
    specialization_register_drop.grid(row=7, column=1, pady=(4,0))
    specialization_register_drop.current(0)
    schoolship_register_drop = ttk.Combobox(frame_register, value=study_schoolarships)
    schoolship_register_drop.grid(row=8, column=1, pady=(4,0))
    schoolship_register_drop.current(0)
    year_register_drop = ttk.Combobox(frame_register, value=study_years)
    year_register_drop.grid(row=9, column=1, pady=(4,0))
    year_register_drop.current(0)

    submit_button_register = Button(frame_register, text="Inregistrare", command=register_database_function)
    submit_button_register.grid(row=10, column=0, columnspan=2, pady=10, ipadx=125)


def login_frame_show():
    global login_frame
    login_frame = LabelFrame(root, padx=30, pady=80)
    login_frame.grid(row=0, column=0, padx=540, pady=200)

    login_title = Label(login_frame, text="Schedule App", font=("Helvetica", 36))
    login_title.grid(row=0, column=0, columnspan=2)

    # Label Texts pentru Login
    username_login_label = Label(login_frame, text="Username: ")
    username_login_label.grid(row=1, column=0, pady=(30, 0))
    password_login_label = Label(login_frame, text="Password: ")
    password_login_label.grid(row=2, column=0)

    global username_login_input
    global password_login_input
    # Input fields pentru Login
    username_login_input = Entry(login_frame, width=30)
    username_login_input.grid(row=1, column=1, pady=(30, 0))
    password_login_input = Entry(login_frame, width=30, show="*")
    password_login_input.grid(row=2, column=1)

    # Buttons pentru Login
    global register_button_login
    log_button_login = Button(login_frame, text="Logare", command=login_function)
    log_button_login.grid(row=3, column=0, columnspan=2, ipadx=115, pady=5)
    register_button_login = Button(login_frame, text="Inregistrare", command=register_window_show)
    register_button_login.grid(row=4, column=0)
    forget_button_login = Button(login_frame, text="Recuperare parola")
    forget_button_login.grid(row=4, column=1, ipadx=36)


login_frame_show()
conn.commit()
conn.close()
root.mainloop()

