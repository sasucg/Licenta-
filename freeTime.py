from tkinter import *
from datetime import date, datetime, timedelta
import sqlite3
from tkinter import messagebox, ttk, filedialog, tix
from tkinter.tix import Balloon

from PIL import ImageTk, Image
import bcrypt
import ast
from tkcalendar import *

import requests
from io import BytesIO
import json


root = tix.Tk()
root.title("Sas's Plan Program  ")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("1400x800")
root.resizable(False, False)

b_image = Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/background/back1.jpg")
b_image = b_image.resize((1400, 800), Image.ANTIALIAS)
background_image = ImageTk.PhotoImage(b_image)
background_label = Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Functia verifica daca toate fieldurile din register card sunt completate
def verify_fields_completed():
    fields_ok = 1
    if first_name_register_input.get() == "" or last_name_register_input.get() == "" or username_register_input.get() == "" or password_register_input.get() == "" or email_register_input.get() == "":
        response = messagebox.showerror("Eroare!", "Nu ați completat toate câmpurile!")
        fields_ok = 0
    return fields_ok


# Functia verifica daca un user se afla sau nu in baza de date
def user_does_exists(user):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * from users")
    users_database = cursor.fetchall()
    exists = "missing"
    for user_database in users_database:
        if user_database[2] == user:
            exists = "found"
            break
    conn.commit()
    conn.close()
    return exists


# Functia verifica daca emailul introdus in register window este valid pentru inregistrare
def verify_email_format(email):
    email_format = "unknownformat"
    if '@' in email and '.' in email:
        email_parts = email.split("@")
        if len(email_parts[0]) >= 6 and len(email_parts[0]) < 30 and len(email_parts[1]) >= 6:
            email_format = "emailformat"

    return email_format


# Functia verifica daca toate datele introduse pentru inregistrare sunt valide si introduce datele in tabela users
# si parolele criptate in tabela parole
def register_database_function(event=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    first_name_register_label.config(fg="black")
    last_name_register_label.config(fg="black")
    username_register_label.config(fg="black")
    password_register_label.config(fg="black")
    email_register_label.config(fg="black")

    if verify_fields_completed() == 0:
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
    elif len(first_name_register_input.get()) > 15:
        messagebox.showerror("Error!", "Prenumele contine multe caractere!")
    elif len(last_name_register_input.get()) > 15:
         messagebox.showerror("Error!", "Prenumele contine multe caractere!")
    elif len(username_register_input.get()) < 6 or len(username_register_input.get()) > 30:
        messagebox.showerror("Error!", "Username are prea putine sau prea multe caractere!")
    elif user_does_exists(username_register_input.get()) != "missing":
        messagebox.showerror("Error!", "Username deja folosit!")
    elif len(password_register_input.get()) < 7:
        messagebox.showerror("Error!", "Parola trebuie sa contina minim 7 caractere!")
    elif verify_email_format(email_register_input.get()) == "emailformat":
        cursor.execute("INSERT INTO users VALUES (:f_name, :l_name, :username, :email, :data_inregistrare, :program, :domeniu, :specializare, :year, :path_pic)",
                       {
                           'f_name': first_name_register_input.get(),
                           'l_name': last_name_register_input.get(),
                           'username': username_register_input.get(),
                           'email': email_register_input.get(),
                           'data_inregistrare': date.today(),
                           'program': program_register_drop.get(),
                           'domeniu': profile_register_drop.get(),
                           'specializare': specialization_register_drop.get(),
                           'year': year_register_drop.get(),
                           'path_pic': "C:/Users/lenovo/PycharmProjects/LicentaSasu/images/defaultprofilepicture/1.jpg"
                       })

        sql_query = """SELECT oid FROM users WHERE username=?"""
        cursor.execute(sql_query, (username_register_input.get(),))
        registered_user_original_id = cursor.fetchone()
        registered_user_pwd =  password_register_input.get().encode("utf-8")
        registered_user_salt = bcrypt.gensalt()
        registered_user_hashpwd = bcrypt.hashpw(registered_user_pwd, registered_user_salt)

        cursor.execute("INSERT INTO parole VALUES (:user_id, :hashpass)",
                    {
                    'user_id': registered_user_original_id[0],
                    'hashpass': registered_user_hashpwd.decode()
                    })

        conn.commit()
        conn.close()
        response = messagebox.showinfo("Info!", "Înregistrarea a avut loc cu succes! ")
        if response == "ok":
            back_to_login_screen()
    else:
        messagebox.showerror("Error!", "Emailul are formatul incorect!!")


# Functia este handle pentru login button, daca username si parola sunt corecte, ne logam, altfel primim eroare.
def login_function(event=None):
    # username_login_input.insert(0, "sasuke")
    # password_login_input.insert(0, "adminadmin")
    if password_login_input.get() == "" or username_login_input.get() == "":
        messagebox.showerror("Eroare", "Introduceți ambele date necesare autentificării!")
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        sql_query = """SELECT oid, username FROM users WHERE username = ?"""
        cursor.execute(sql_query, (username_login_input.get(),))
        username_database = cursor.fetchone()

        conn.commit()
        conn.close()
        if username_database != None:
            connpwd = sqlite3.connect('users.db')
            cursorpwd = connpwd.cursor()

            sql_query =  """SELECT hashpass FROM parole WHERE user_id=?"""
            cursorpwd.execute(sql_query,(username_database[0],))

            hashpass_database = cursorpwd.fetchone()
            connpwd.commit()
            connpwd.close()

            attempt_password = password_login_input.get()

            if bcrypt.checkpw(attempt_password.encode("utf-8"), hashpass_database[0].encode("utf-8")) == True:
                login_frame.grid_forget()
                logged_in_function()
            else:
                messagebox.showerror("Eroare!", "Datele introduse sunt invalide! Reîncercați!")
        else:
            messagebox.showerror("Eroare!", "Datele introduse sunt invalide! Reîncercați!")



# Functia este handle pentru logout button, daca dorim sa ne delogam, ne intoarcem la login_frame_show iar celelalte
# ferestre deschise sunt distruse.
def logout_function():
    response = messagebox.askyesno("Deconectare", "Doriți să vă deconectați?")
    if response == True:
        logged_in_frame.destroy()
        # profile_window.destroy()
        # courses_window.destroy()
        # hobbies_window.destroy()
        # grades_window.destroy()

        application_on()
        username_login_input.config(text="")
        password_login_input.config(text="")
    else:
        return


# Functia furnizeaza first name-ul si original id-ul userului logat
def querry_data_logged_user(logged_user):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    sql_query = """SELECT oid, prenume, nume, username, email, data_inregistrare, program, domeniu, specializare, an FROM users WHERE username = ?"""
    cursor.execute(sql_query, (logged_user,))
    user_database = cursor.fetchone()

    conn.commit()
    conn.close()
    return user_database


#Functia furnizeaza semestrul actual in functie de data in care ne aflam: semestrul 1 / 2 / vacanta de vara
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
    # AICI VA TREBUI current_semester
    return 2


# Functia cauta in baza de date materiile corespunzatoare: specializarii userului, anul si semestrul
def get_current_courses(specialization, year, semester):
    conn = sqlite3.connect('materii.db')
    cursor = conn.cursor()
    courses_database_as_list = []
    sql_query = """SELECT nume FROM materii WHERE specializare = ? AND an = ? AND semestru = ?"""
    cursor.execute(sql_query, (specialization, year, semester))
    courses_database = cursor.fetchall()
    for course in courses_database:
        courses_database_as_list.append(course[0])
    conn.commit()
    conn.close()

    return courses_database_as_list


def commit_failures_to_database():
    valid_failure = True
    dropdowns_values = []
    for dropdown in failed_exams_list_dropdowns:
        dropdowns_values.append(dropdown.get())

    error = ""
    for value in dropdowns_values:
        if value == "Stergere":
            error = "'Stergere' nu poate fi o restanta"
            valid_failure = False
            break

    failed_exams_values = [item[0] for item in failed_exams_list]
    if error == "":
        if len(set(dropdowns_values)) == len(dropdowns_values):
            for value in dropdowns_values:
                if value in failed_exams_values:
                    valid_failure = False
                    error = "Nu puteti avea mai multe restante la aceeasi materie1"
                    break;
        else:
            valid_failure = False
            error = "Nu puteti avea mai mutle restante la aceeasi materie2"


    if valid_failure == True:
        commited_failed_exams = []
        for failed in failed_exams_list:
            commited_failed_exams.append(failed)

        for dropdown in failed_exams_list_dropdowns:
            commited_failed_exams.append([dropdown.get(), "--/--/--"])

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        sql_delete = "DELETE from restante WHERE user_id=?"
        cursor.execute(sql_delete, (logged_original_id,))
        for failed in commited_failed_exams:
            sql_insert = """INSERT INTO restante(user_id, materie, data) VALUES(?, ?, ?)"""
            com_insert =  logged_original_id, failed[0], failed[1]
            cursor.execute(sql_insert, com_insert)

        conn.commit()
        conn.close()
        messagebox.showinfo('Info', "Restantele au fost salvate")
        edit_failed_button.config(state=NORMAL)
        edit_failed_frame.forget()
        failed_frame.forget()
        show_failed_courses()
    else:
        messagebox.showerror("Error", error)



def add_failed_course():
    save_failed_button.config(state=NORMAL)
    current_semester = get_current_semester()
    current_year = get_year_as_int(logged_year)

    if current_semester == 2:
        semesters_to_show = current_year * current_semester
    else:
        semesters_to_show = current_year * 2 - 1

    semesters_shown = 0
    an = "I"
    semestru = 1
    past = []
    past.append("Stergere")
    while semesters_shown != semesters_to_show:
        if (logged_specialization == "Mate-Info" or logged_specialization == "Mate-Aplicata") and an == "I":
            user_past_courses = get_current_courses("Matematica", an, semestru)
            user_past_grades = get_grades_from_database(user_past_courses)
            for course in user_past_courses:
                past.append(course)
        else:
            user_past_courses = get_current_courses(logged_specialization, an, semestru)
            user_past_grades = get_grades_from_database(user_past_courses)
            for course in user_past_courses:
                past.append(course)

        semesters_shown += 1
        if semesters_shown == 2:
            an = "II"
        if semesters_shown == 4:
            an = "III"
        if semesters_shown == 6:
            an = "IV"
        semestru += 1
        if semestru == 3:
            semestru = 1

    failed_dropdown = ttk.Combobox(edit_failed_frame, value=past)
    failed_dropdown.pack()
    failed_dropdown.current(0)
    failed_exams_list_dropdowns.append(failed_dropdown)


def delete_failed_course(vars):
    for var in reversed(vars):
        if var.get() == 1:
            failed_exams_list.pop(vars.index(var))
            failed_course_checkboxes[vars.index(var)].forget()
            failed_course_checkboxes.pop(vars.index(var))

    for var in reversed(vars):
        if var.get() == 1:
            vars.pop(vars.index(var))

    for dropdown in reversed(failed_exams_list_dropdowns):
        if dropdown.get() == "Stergere":
            dropdown.destroy()
            failed_exams_list_dropdowns.pop(failed_exams_list_dropdowns.index(dropdown))


def edit_failed_courses():
    global edit_failed_frame
    edit_failed_frame = LabelFrame(courses_window, text="Editare Restante")
    edit_failed_frame.pack(fill="both")
    edit_failed_button.config(state=DISABLED)

    edit_options_failed = LabelFrame(edit_failed_frame, bd=0)
    edit_options_failed.pack()
    global save_failed_button
    save_failed_button = Button(edit_options_failed, text="Salvează", bd=1, command=commit_failures_to_database)
    save_failed_button.pack(side=LEFT)
    add_failed = Button(edit_options_failed, text="Adăugare", command=add_failed_course, bd=1)
    add_failed.pack(side=LEFT)
    delete_failed = Button(edit_options_failed, text="Ștergere", bd=1, command=lambda: delete_failed_course(vars))
    delete_failed.pack(side=RIGHT)

    global failed_course_checkboxes
    failed_course_checkboxes = []
    vars = []
    if failed_exams_list != []:
        for failed_course in failed_exams_list:
            var = IntVar()
            vars.append(var)
            failed_course_checkbox = Checkbutton(edit_failed_frame, text=failed_course[0], variable=var)
            failed_course_checkbox.pack(anchor = "w")
            failed_course_checkboxes.append(failed_course_checkbox)


def show_failed_courses():
    global failed_exams_list
    global failed_exams_list_dropdowns
    global failed_frame
    failed_exams_list = []
    failed_exams_list_dropdowns = []
    failed_frame = LabelFrame(courses_window, text="Restante", font=("Helvetica", 13))
    failed_frame.pack(fill="both")
    global edit_failed_button
    edit_failed_button = Button(failed_frame, text="Manager Restante", command=edit_failed_courses)

    failed_exams_list = get_exam_list_from_database("daterestante")
    if failed_exams_list != []:
        for failed_course in failed_exams_list:
            failed_course_label = Label(failed_frame, text=failed_course[0])
            failed_course_label.pack()
        edit_failed_button.pack()
    else:
        no_failure_label = Label(failed_frame, text="Felicitări! Nu ai restanțe!")
        no_failure_label.pack()
        edit_failed_button.config(text="Manager Restante")
        edit_failed_button.pack()


# Functia apeleaza functia care furnizeaza materiile curente si le afiseaza
# TO BE DESIGNED000003
def show_current_courses():
    global courses_window
    courses_window = Toplevel()
    courses_window.title("Materii")
    courses_window.geometry("450x500")

    courses_button_menu.config(state=DISABLED)
    courses_window.protocol("WM_DELETE_WINDOW", lambda: buttons_available(courses_window, courses_button_menu))

    current_semester = get_current_semester()

    if current_semester == 0:
        summer = Label(courses_window, text="Vacanta placuta!", font=("Helvetica", 13))
        summer.pack()
    else:
        courses_database = get_current_courses(logged_specialization, logged_year, current_semester)
        courses_frame = LabelFrame(courses_window, text="Materii An "+logged_year+", semestrul "+str(current_semester), font=("Helvetica", 13))
        courses_frame.pack(fill="both")
        for course in courses_database:
            course_label = Label(courses_frame, text=course)
            course_label.pack()

        show_failed_courses()


#Functia e folosita in querry_grades pentru a returna valoarea int a unui an, folosita in querry_courses
def get_year_as_int(string_year):
    if string_year == "IV": return 4
    if string_year == "III": return 3
    if string_year == "II": return 2
    if string_year == "I": return 1


# Functia e folosita in querry_grades pentru a ne permite sa apelam querry_courses dupa an(string) / semestru
def get_year_as_string(int_year):
    if int_year == 1: return "I"
    if int_year == 2: return "II"
    if int_year == 3: return "III"


# Functia furnizeaza un vector de note care corespunde vectorului user past courses
def get_grades_from_database(user_past_courses):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    grades = []

    for i in range(len(user_past_courses)):
        sql_query = """SELECT nota FROM note WHERE id_user = ? AND nume_materie = ?"""
        cursor.execute(sql_query, (logged_original_id, user_past_courses[i]))
        grade_database = cursor.fetchone()
        try:
            grades.append(grade_database[0])
        except:
            grades.append(None)

    conn.commit()
    conn.close()
    return grades



# Functia actualizeaza notele in baza de date
def commit_grades_database(course_dropdowns, user_past_courses):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    commited_user_grades = []

    for i in range(0, len(user_past_courses)):
        commited_user_grades.append(course_dropdowns[i].get())

    for i in range(len(user_past_courses)):
        if commited_user_grades[i] != "-":
            sql_delete = "DELETE from note WHERE id_user=? and nume_materie=?"
            com_delete = logged_original_id, user_past_courses[i]
            cursor.execute(sql_delete, com_delete)
            sql_insert = """INSERT INTO note(id_user, nume_materie, nota) VALUES(?, ?, ?)"""
            com_insert =  logged_original_id, user_past_courses[i], commited_user_grades[i]
            cursor.execute(sql_insert, com_insert)

    conn.commit()
    conn.close()

    response = messagebox.showinfo("Saved!", "Modificarile au fost salvate!")
    if response == "ok":
        buttons_available(grades_window, reportcard_button_menu)


# Functia afiseaza pe grades_window materiile si notele pe care le-am obtinut, din trecut pana in prezent.
def show_report_card():
    global grades_window
    grades_window = Toplevel()
    grades_window.title("Carnet de note")

    reportcard_button_menu.config(state=DISABLED)
    grades_window.protocol("WM_DELETE_WINDOW", lambda: buttons_available(grades_window, reportcard_button_menu))

    current_semester = get_current_semester() # Aflam semestrul in care suntem
    current_year = get_year_as_int(logged_year) # Luam anul in care suntem ca int

    # Aflam cate semestre trebuie sa postam
    if current_semester == 2:
        semesters_to_show = current_year * current_semester
    else:
        semesters_to_show = current_year * 2 - 1

    # Luam notele la materiile din trecut + cele din prezent unele vor fi None
    note = ["-", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    course_dropdowns = [] # Vectorul in care tinem casutele de tip dropdown si valorile acestora. Casutele corespund materiei i din vecctorul user_past_courses
    semesters_shown = 0
    an = "I"
    semestru = 1
    past = []
    linie = 0 # Linia ne ajuta la postarea elementelor in fereastra

    while semesters_shown != semesters_to_show:
        label = Label(grades_window, text="Anul "+an+" semestrul "+str(semestru), font=("Times New Roman", 15, "italic"), fg="#0099cc")
        label.grid(row=linie, column=0, columnspan=2)
        linie += 1

        if (logged_specialization == "Mate-Info" or logged_specialization == "Mate-Aplicata") and an == "I":
            user_past_courses = get_current_courses("Matematica", an, semestru)
            user_past_grades = get_grades_from_database(user_past_courses)
            for course in user_past_courses:
                past.append(course)
        else:
            user_past_courses = get_current_courses(logged_specialization, an, semestru)
            user_past_grades = get_grades_from_database(user_past_courses)
            for course in user_past_courses:
                past.append(course)

        for i in range(0, len(user_past_courses)):  # Pentru fiecare curs, il postam in stanga si nota acestuia in dreapta
            course_text_label = Label(grades_window, text=user_past_courses[i])
            course_text_label.grid(row=linie, column=0, sticky="w", padx=(10,5))

            course_dropdown = ttk.Combobox(grades_window, value=note)
            if user_past_grades[i] == None:
                course_dropdown.current(0)
            else:
                course_dropdown.current(user_past_grades[i])

            course_dropdown.grid(row=linie, column=1, padx=(0,10))
            course_dropdowns.append(course_dropdown)
            linie += 1

        semesters_shown += 1
        if semesters_shown == 2:
            an = "II"
        if semesters_shown == 4:
            an = "III"
        if semesters_shown == 6:
            an = "IV"
        semestru += 1
        if semestru == 3:
            semestru = 1

    save_changes = Button(grades_window, text="Salvează", command=lambda: commit_grades_database(course_dropdowns, past), padx=150, bd=1)
    save_changes.grid(row=linie+1, column=0, columnspan=2, pady=20)



# Functia intoarce hobbyurile unui user, folosita pentru a afisa hobbyurile care au fost selectate in trecut
def get_hobbies_list_from_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    selected_hobbies_from_database = []
    sql_query = """SELECT hobby, frecventa  FROM usershobbies WHERE id_user = ?"""
    cursor.execute(sql_query, (logged_original_id,))
    hobbies_list_db = cursor.fetchall()
    print(hobbies_list_db)

    standard_hobbies_list = []
    for hobby in hobbies_list_db:
        standard_hobbies_list.append([hobby[0], hobby[1]])

    return standard_hobbies_list


def deselect_hobby(i):
    hobby_images_button_list[i].config(width = 200, height= 150, command=lambda: select_hobby(i))
    hobby_images_button_list[i].grid(padx=0, pady=0)
    selected_hobbies_list.remove(i)
    continue_button.config(state=DISABLED)
    progres_value = progress_bar_hobbies['value']
    progress_bar_hobbies.config(value=progres_value - 25)


# Functia selecteaza un hobby: ii schima dimensiunile si paddingul + il adauga in lista de hobby-uri selectate
def select_hobby(i):
    if len(selected_hobbies_list) + len(another_hobbies_list) < 4:
        selected_hobbies_list.append(i)
        hobby_images_button_list[i].config(width=150, height=100, command=lambda: deselect_hobby(i))
        hobby_images_button_list[i].grid(padx=25, pady=25)
        progres_value = progress_bar_hobbies['value']
        progress_bar_hobbies.config(value=progres_value+25)
    else:
        messagebox.showinfo("Info", "Aveti deja 4 ocupații introduse!")

    if len(selected_hobbies_list) + len(another_hobbies_list) == 4:
        continue_button.config(state=NORMAL)

def get_frequency_as_int(freq):
    if freq == "Foarte rar":
        return 1
    if freq == "Rar":
        return 2
    if freq == "Uneori":
        return 3
    if freq == "Des":
        return 4
    if freq == "Foarte des":
        return 5

def get_frequency_as_string(freq):
    if freq == 1:
        return "Foarte rar"
    if freq == 2:
        return "Rar"
    if freq == 3:
        return "Uneori"
    if freq == 4:
        return "Des"
    if freq == 5:
        return "Foarte des"

def get_hobby_name_from_database(i):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("Select denumire_hobby from hobby where index_imagine = ?", (str(i),))
    denumire = cursor.fetchone()

    conn.close()
    return denumire[0]


def get_hobby_id_from_database(name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("Select index_imagine from hobby where denumire_hobby = ?", (name,))
    index = cursor.fetchone()
    conn.close()
    if index == None:
        return 'notfound'
    else:
        return index[0]


def user_has_hobbies():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id_user FROM usershobbies")
    users = cursor.fetchall()

    conn.commit()
    conn.close()
    user_has = False
    for user in users:
        if user[0] == logged_original_id:
            user_has = True
    return user_has


def commit_hobbies():
    commited_selected_list = []
    i = 0

    for selected in selected_hobbies_list:
        denumire = get_hobby_name_from_database(selected)
        commited_selected_list.append([denumire, get_frequency_as_int(selected_hobbies_freq_combos[i].get())])
        i += 1

    for another in another_hobbies_list:
        commited_selected_list.append(another)

    user_hobbies_bool = user_has_hobbies()
    if len(selected_hobbies_list) + len(another_hobbies_list) == 4:
        if user_hobbies_bool == True:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            sql_delete = "DELETE from usershobbies WHERE id_user=?"
            cursor.execute(sql_delete, (logged_original_id,))
            for hobby in commited_selected_list:
                cursor.execute("INSERT INTO usershobbies VALUES (:id_user, :hob, :frec)",
                               {
                                   'id_user': logged_original_id,
                                   'hob': hobby[0],
                                   'frec': hobby[1]
                               })
            response = messagebox.showinfo("Info", "Modificările au fost salvate!")

            if response == "ok":
                hobbies_edit_window.destroy()
                your_hobbies_frame.destroy()
                try:
                    session_program_window.destroy()
                    messagebox.showinfo("Info!",
                                        "Ocupațiile utilizatorului au fost schimbate, acest lucru duce la terminarea programului de sesiune")
                except:
                    pass
                post_users_hobbies(commited_selected_list)

            conn.commit()
            conn.close()
        else:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            for hobby in commited_selected_list:
                cursor.execute("INSERT INTO usershobbies VALUES (:id_user, :hob, :frec)",
                               {
                                   'id_user': logged_original_id,
                                   'hob': hobby[0],
                                   'frec': hobby[1]
                               })
            response = messagebox.showinfo("Info", "Modificările au fost salvate123!")

            if response == "ok":

                hobbies_edit_window.destroy()
                try:
                    your_hobbies_frame.destroy()
                except:
                    pass
                post_users_hobbies(commited_selected_list)
            conn.commit()
            conn.close()



def insert_hobby(type):
    if type == "another":
        if len(selected_hobbies_list) + len(another_hobbies_list) < 4:
            if another_hobby_combobox_freq.get() == "" or another_hobby_entry_name.get() == "":
                if another_hobby_entry_name.get() == "":
                    another_hobby_label_name.config(fg="red")
                    messagebox.showerror("Error", "Nu ati introdus denumirea hobby-ului!")
                    another_hobby_label_freq.config(fg="black")
                else:
                    another_hobby_label_name.config(fg="black")
                    another_hobby_label_freq.config(fg="red")
                    messagebox.showerror("Error", "Nu ati introdus frecventa hobby-ului!")
            else:
                another_hobbies_list.append([another_hobby_entry_name.get(), get_frequency_as_int(another_hobby_combobox_freq.get())] )
                progres_value = progress_bar_hobbies['value']
                progress_bar_hobbies.config(value=progres_value + 25)
                another_hobby_entry_name.delete(0, END)
        else:
            messagebox.showerror("Error", "Ati introdus deja 4 hobby-uri!")
        if len(selected_hobbies_list) + len(another_hobbies_list) == 4:
            continue_button.config(state=NORMAL)

    if type == "selected":
        another_hobby_frame.grid_forget()

        global selected_hobbies_freq_combos
        selected_hobbies_freq_combos = []
        c = 0
        for but in hobby_images_button_list:
            if hobby_images_button_list.index(but) not in selected_hobbies_list:
                but.grid_forget()
            else:
                but.grid(row=0, column=c)
                but.config(command=NONE)
                denumire = get_hobby_name_from_database(hobby_images_button_list.index(but))
                label = Label(hobbies_list_frame, text=denumire)
                label.grid(row=1, column=c)
                combo = ttk.Combobox(hobbies_list_frame, value=["Foarte rar", "Rar", "Uneori", "Des", "Foarte des"])
                combo.grid(row=2, column=c)
                combo.current(0)
                selected_hobbies_freq_combos.append(combo)
            c += 1

        continue_button.config(command=commit_hobbies)


def close_edit(type):
    if type == "hobby":
        hobbies_edit_window.destroy()
        edit_hobbies_button.config(state=NORMAL)
    if type == "profil":
        edit_user_profile_frame.destroy()
        edit_profile_button.config(state=NORMAL)


def edit_hobbies():
    global hobbies_edit_window
    hobbies_edit_window = LabelFrame(hobbies_window, text="Noile ocupații")
    hobbies_edit_window.pack()
    try:
        edit_hobbies_button.config(state=DISABLED)
    except:
        pass
    welcome_pick_hobbies = Label(hobbies_edit_window, text="Alege sau introdu 4 ocupații preferate!", font=("Helvetica", 12))
    welcome_pick_hobbies.grid(row=0, column=0)

    global close_button
    close_button = Button(hobbies_edit_window, text="X", command=lambda: close_edit("hobby"), padx=10, bd=1, font=("Helvetica", 10, "bold"))
    close_button.grid(row=0, column=0, sticky="E", pady=(0,10))

    close_button.bind("<Enter>", hover)
    close_button.bind("<Leave>", leave)

    global hobbies_list_frame
    hobbies_list_frame = LabelFrame(hobbies_edit_window, bd=0)
    hobbies_list_frame.grid(row=1, column=0)
    global selected_hobbies_list
    selected_hobbies_list = []

    global hobby_images_button_list
    hobby_images_button_list = []

    for i in range(21):
        image = Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/" + str(i) + ".jpg")
        image = image.resize((200, 150), Image.ANTIALIAS)
        hobby_img_to_post = ImageTk.PhotoImage(image)

        hobby_images_button_list.append(i)
        if i not in selected_hobbies_list:
            hobby_images_button_list[i] = Button(hobbies_list_frame, image=hobby_img_to_post, command=lambda index=i: select_hobby(index))
        else:
            hobby_images_button_list[i] = Button(hobbies_list_frame, image=hobby_img_to_post, command=lambda index=i: deselect_hobby(index), width=150, height=100)

        hobby_images_button_list[i].image = (hobby_img_to_post)

    r = 1
    c = 0
    for but in hobby_images_button_list:
        if c == 7:
            r += 1
            c = 0
        if hobby_images_button_list.index(but) in selected_hobbies_list:
            but.grid(row=r, column=c, padx=25, pady=25)
        else:
            but.grid(row=r, column=c)
        c += 1

    global progress_bar_hobbies
    progress_bar_hobbies = ttk.Progressbar(hobbies_edit_window, length=400, orient=HORIZONTAL, maximum=100, value=0)
    progress_bar_hobbies.grid(row=2, column=0)

    possible_freq = ["Foarte rar", "Rar", "Uneori", "Des", "Foarte des"]
    global another_hobby_label_name
    global another_hobby_label_freq
    global another_hobby_frame
    another_hobby_frame = LabelFrame(hobbies_edit_window)
    another_hobby_frame.grid(row=3, column=0)
    another_hobby_label = Label(another_hobby_frame, text="Dacă hobby-ul tău nu se regăsește în lista de mai sus, îl poți introduce:")
    another_hobby_label.grid(row=0, column=0, columnspan=2)
    another_hobby_label_name = Label(another_hobby_frame, text="Denumire: ")
    another_hobby_label_name.grid(row=1, column=0)
    another_hobby_label_freq = Label(another_hobby_frame, text="Frecventă: ")
    another_hobby_label_freq.grid(row=2, column=0)

    global another_hobby_entry_name
    global another_hobby_combobox_freq
    global another_hobbies_list
    another_hobbies_list = []
    another_hobby_entry_name = Entry(another_hobby_frame, width=50)
    another_hobby_entry_name.grid(row=1, column=1)
    another_hobby_combobox_freq = ttk.Combobox(another_hobby_frame, value=possible_freq, width=47)
    another_hobby_combobox_freq.grid(row=2, column=1)
    another_hobby_combobox_freq.current(0)
    another_hobby_button = Button(another_hobby_frame, text="Introdu", command=lambda: insert_hobby("another"))
    another_hobby_button.grid(row=0, column=2)

    global continue_button
    continue_button = Button(hobbies_edit_window, text="Continuă", command=lambda: insert_hobby("selected"), state=DISABLED, padx=160)
    continue_button.grid(row=5, column=0, pady=(5,0))


def post_users_hobbies(hobbies_list):
    global your_hobbies_frame
    your_hobbies_frame = LabelFrame(hobbies_window)
    your_hobbies_frame.pack(padx=315, pady=(10,10))

    your_hobbies_label = Label(your_hobbies_frame, text="Ocupații preferate:")
    your_hobbies_label.grid(row=0, column=0)
    col = 0
    for hobby in hobbies_list:
        img_index = get_hobby_id_from_database(hobby[0])
        if img_index != 'notfound':
            image = Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/" + str(img_index) + ".jpg")
            image = image.resize((200, 150), Image.ANTIALIAS)
            hobby_img_to_post = ImageTk.PhotoImage(image)
            hobby_image = Label(your_hobbies_frame, image=hobby_img_to_post)
            hobby_image.image = hobby_img_to_post
            hobby_image.grid(row=1, column=col)

            hobby_text = Label(your_hobbies_frame, text=hobby[0])
            hobby_text.grid(row=2, column=col)
            hobby_frequency = Label(your_hobbies_frame, text=get_frequency_as_string(hobby[1]))
            hobby_frequency.grid(row=3, column=col)
            col += 1
        else:
            try:
                api_request = requests.get("https://pixabay.com/api/?key=17121996-f951a11578879a7e7f8ea3d39&q=" + hobby[0] + "&image_type=photo&lang=ro&per_page=10")
                api = json.loads(api_request.content)
                img_url = api['hits'][5 ]['largeImageURL']

                response = requests.get(img_url)
                image = Image.open(BytesIO(response.content))
                image = image.resize((200, 150), Image.ANTIALIAS)
                hobby_img_to_post = ImageTk.PhotoImage(image)
                hobby_image = Label(your_hobbies_frame, image=hobby_img_to_post)
                hobby_image.image = hobby_img_to_post
                hobby_image.grid(row=1, column=col)

                hobby_text = Label(your_hobbies_frame, text=hobby[0])
                hobby_text.grid(row=2, column=col)
                hobby_frequency = Label(your_hobbies_frame, text=get_frequency_as_string(hobby[1]))
                hobby_frequency.grid(row=3, column=col)
                col += 1
            except:
                hobby_text = Label(your_hobbies_frame, text=hobby[0], width=30, height=10, bd=1)
                hobby_text.grid(row=1, column=col)
                hobby_frequency = Label(your_hobbies_frame, text=get_frequency_as_string(hobby[1]))
                hobby_frequency.grid(row=3, column=col)
                col += 1

    global edit_hobbies_button
    edit_hobbies_button = Button(your_hobbies_frame, text="Editează", command=edit_hobbies, padx=160, bd=1)
    edit_hobbies_button.grid(row=4, column=0, columnspan=4, pady=(5,0))


def show_users_hobbies():
    global hobbies_window
    hobbies_window = Toplevel()
    hobbies_window.title("Ocupațiile mele")

    hobbies_button_menu.config(state=DISABLED)
    hobbies_window.protocol("WM_DELETE_WINDOW", lambda: buttons_available(hobbies_window, hobbies_button_menu))

    global hobbies_list
    hobbies_list = get_hobbies_list_from_database()

    if len(hobbies_list) == 0:
        edit_hobbies()
    else:
        post_users_hobbies(hobbies_list)




def check_if_hours_valid(hours_start, hours_over):
    for hour_s, hour_o in zip(hours_start, hours_over):
        if (hour_s >= hour_o):
            error_message = "Ora de inceput a unei ore de curs nu poate fi mai mare decat cea de sfarsit!"
            return False, error_message

    if len(hours_start) > len(set(hours_start)) or len(hours_over) > len(set(hours_over)):
        error_message = "Nu puteti incepe sau sfarsi doua ore de curs in acelasi timp!"
        return False, error_message

    interval_list = list(zip(hours_start, hours_over))
    interval_list = sorted(interval_list, key=lambda x: x[1])
    for i in range(0, len(interval_list)-1):
        if interval_list[i+1][0] < interval_list[i][1]:
            error_message = "Intervalele orelor de curs se intersecteaza!"
            return False, error_message
    return True, None


def commit_courses_of_day(Day):
    courses_list_for_day = []
    hours_start = []
    hours_over = []

    list_index=0
    for list in courses_drop_list_for_day:
        courses_list_for_day.append([])
        for object in list:
            courses_list_for_day[list_index].append(object.get())
        list_index += 1

    for course in courses_list_for_day:
        hours_start.append(int(course[2]))
        hours_over.append(int(course[3]))

    hours_are_valid, error_message = check_if_hours_valid(hours_start, hours_over)

    if hours_are_valid == True:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        courses_list_for_day = sorted(courses_list_for_day, key = lambda x: int(x[2])) # Sortam lista de liste dupa ora de start a orei de curs

        sql_delete = "DELETE from oredecurs where id_user = ? and zi = ?"
        cursor.execute(sql_delete, (logged_original_id, Day))
        print(Day)
        for course in courses_list_for_day:
            print(course)
            sql_insert = """INSERT INTO oredecurs(id_user, zi, tip_curs, nume_curs, ora_inceput, ora_sfarsit) VALUES(?, ?, ?, ?, ?, ?)"""
            com_insert = logged_original_id, Day.lower(), course[0], course[1], course[2], course[3]
            cursor.execute(sql_insert, com_insert)

        messagebox.showinfo("Info", "Modificarile au fost salvate")
        conn.commit()
        conn.close()
        edit_day_frame.destroy()
        post_courses_to_timetable()
    else:
        messagebox.showerror("Erorr", message=error_message)



def add_course_for_edit():
    if this_many_courses.get() != "" and int(this_many_courses.get()) <= 6:
        number_of_courses_for_day = int(this_many_courses.get())

        this_many_courses.destroy()
        how_many_courses.destroy()
        add_course_button.config(state=DISABLED)
        save_course_button.config(state=NORMAL)
        course_type_list = [
            "Curs",
            "Laborator",
            "Seminar"
        ]
        # In locul lui 2 trebuei sa fie current_semester
        current_semester = get_current_semester()
        courses_list = get_current_courses(logged_specialization, logged_year, current_semester)
        hours_start = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        hours_over = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        # Lista cursurilor dintr-o zi este globala pentru a putea fi salvata in baza de date in functia save_courses_of_day
        global courses_drop_list_for_day
        courses_drop_list_for_day = []

        course_type_label = Label(edit_day_frame, text="Tipul orei")
        course_type_label.grid(row=1, column=0, padx=(20, 20), pady=(30, 10))
        course_name_label = Label(edit_day_frame, text="Numele orei")
        course_name_label.grid(row=1, column=1, padx=(20, 20), pady=(30, 10))
        course_hour_start_label = Label(edit_day_frame, text="Ora început")
        course_hour_start_label.grid(row=1, column=2, padx=(20, 20), pady=(30, 10))
        course_hour_over_label = Label(edit_day_frame, text="Ora sfârșit")
        course_hour_over_label.grid(row=1, column=3, padx=(20, 20), pady=(30, 10))

        for i in range(0,number_of_courses_for_day):
            course_type_drop = ttk.Combobox(edit_day_frame, value=course_type_list)
            course_type_drop.grid(row=i+2, column=0, pady=(0, 20), padx=(20, 20))
            course_type_drop.current(0)

            course_name_drop = ttk.Combobox(edit_day_frame, value=courses_list)
            course_name_drop.grid(row=i+2, column=1, pady=(0, 20), padx=(20, 20))
            course_name_drop.current(0)

            hour_start_drop = ttk.Combobox(edit_day_frame, value=hours_start)
            hour_start_drop.grid(row=i+2, column=2, pady=(0, 20), padx=(20, 20))
            hour_start_drop.current(0)

            hour_over_drop = ttk.Combobox(edit_day_frame, value=hours_over)
            hour_over_drop.grid(row=i+2, column=3, pady=(0, 20), padx=(20, 20))
            hour_over_drop.current(0)


            courses_drop_list_for_day.append([course_type_drop, course_name_drop, hour_start_drop, hour_over_drop])

    else:
        how_many_courses.config(fg="red")


def edit_courses_day(Day):
    for child in edit_container.winfo_children():
        child.destroy()
    global edit_day_frame
    edit_day_frame = LabelFrame(edit_container, text="Editare "+Day)
    edit_day_frame.pack()

    global save_course_button
    save_course_button = Button(edit_day_frame, text="Salvează", state=DISABLED, command=lambda: commit_courses_of_day(Day), padx=70)
    save_course_button.grid(row=0, column=3, padx=(20,20))

    edit_day_label = Label(edit_day_frame, text="Editează materiile de "+Day)
    edit_day_label.grid(row=0, column=1, columnspan=2)

    # how many si this many sunt globale pentru a putea fi sterse in functia add courses for edit
    global how_many_courses
    how_many_courses = Label(edit_day_frame, text="Câte materii aveți "+Day+"?")
    how_many_courses.grid(row=1, column=0, padx=(20,20))

    global this_many_courses
    this_many_courses = Entry(edit_day_frame, width=60)
    this_many_courses.grid(row=1, column=1)

    global add_course_button
    add_course_button = Button(edit_day_frame, text="Adaugă în orarul de " + Day, command=add_course_for_edit)
    add_course_button.grid(row=0, column=0, padx=(20,20))


def select_courses_for_timetable(day_frame, day):
    for child in day_frame.winfo_children():
        child.destroy()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    linie = 0
    sql_query = "SELECT tip_curs, nume_curs, ora_inceput, ora_sfarsit FROM oredecurs WHERE id_user=? and zi = ?"
    cursor.execute(sql_query, (logged_original_id,day))
    courses_from_database = cursor.fetchall()
    courses_of_day = []
    for course in courses_from_database:
        courses_of_day.append([course[0], course[1], course[2], course[3]])
    if courses_of_day == [] or courses_of_day == None:
        courses_not_found = Label(day_frame, text="Nu ati introdus valorile \n pentru ziua "+day.capitalize())
        courses_not_found.grid(row=0, column=0)
    else:
        for course in courses_of_day:
            course_hours_label = Label(day_frame, text=str(course[2]) + "-" + str(course[3]))
            course_hours_label.grid(row=linie, column=0)
            course_type_label = Label(day_frame, text=course[0])
            course_type_label.grid(row=linie, column=1)
            course_name_label = Label(day_frame, text=course[1])
            course_name_label.grid(row=linie, column=2, sticky="E")
            linie += 1

    conn.close()
    return


def post_courses_to_timetable():
    select_courses_for_timetable(monday_frame, "luni")
    select_courses_for_timetable(tuesday_frame, "marti")
    select_courses_for_timetable(wednesday_frame, "miercuri")
    select_courses_for_timetable(thursday_frame, "joi")
    select_courses_for_timetable(friday_frame, "vineri")


def show_timetable():
    global timetable_window
    timetable_window = Toplevel()
    timetable_window.title("Editarea orarului meu")

    timetable_button_menu.config(state=DISABLED)
    timetable_window.protocol("WM_DELETE_WINDOW", lambda: buttons_available(timetable_window, timetable_button_menu))
    timetable_welcome = Label(timetable_window, text="Orarul meu", font=("Times New Roman", 20, "italic"), fg="#0099cc")
    timetable_welcome.pack(pady=(10,10))

    global timetable_frame
    timetable_frame = LabelFrame(timetable_window)
    timetable_frame.pack()

    global monday_frame
    global tuesday_frame
    global wednesday_frame
    global thursday_frame
    global friday_frame
    monday_frame = LabelFrame(timetable_frame, font=("Halvetica", 20), padx=5, pady=5)
    monday_frame.grid(row=1, column=0, pady=(0,20), sticky="n", padx=30)  # padding outside frame
    tuesday_frame = LabelFrame(timetable_frame, font=("Halvetica", 20), padx=5, pady=5)
    tuesday_frame.grid(row=1, column=1, pady=(0, 20), sticky="n", padx=30)
    wednesday_frame = LabelFrame(timetable_frame, font=("Halvetica", 20), padx=5, pady=5)
    wednesday_frame.grid(row=1, column=2, pady=(0, 20), sticky="n", padx=30)
    thursday_frame = LabelFrame(timetable_frame, font=("Halvetica", 20), padx=5, pady=5)
    thursday_frame.grid(row=1, column=3, pady=(0, 20), sticky="n", padx=30)
    friday_frame = LabelFrame(timetable_frame, font=("Halvetica", 20), padx=5, pady=5)
    friday_frame.grid(row=1, column=4, pady=(0, 20), sticky="n", padx=30)

    monday_edit_button = Button(timetable_frame, text="Luni", command=lambda: edit_courses_day("Luni"), bd=0, font=("Times New Roman", 13, "italic"), fg="#0099cc")
    monday_edit_button.grid(row=0, column=0, padx=30, pady=(10,0))
    tuesday_edit_button = Button(timetable_frame, text="Marți", command=lambda: edit_courses_day("Marti"), bd=0, font=("Times New Roman", 13, "italic"), fg="#0099cc")
    tuesday_edit_button.grid(row=0, column=1, padx=30, pady=(10,0))
    wednesday_edit_button = Button(timetable_frame, text="Miercuri", command=lambda: edit_courses_day("Miercuri"), bd=0, font=("Times New Roman", 13, "italic"), fg="#0099cc")
    wednesday_edit_button.grid(row=0, column=2, padx=30, pady=(10,0))
    thursday_edit_button = Button(timetable_frame, text="Joi", command=lambda: edit_courses_day("Joi"), bd=0, font=("Times New Roman", 13, "italic"), fg="#0099cc")
    thursday_edit_button.grid(row=0, column=3, padx=30, pady=(10,0))
    friday_edit_button = Button(timetable_frame, text="Vineri", command=lambda: edit_courses_day("Vineri"), bd=0, font=("Times New Roman", 13, "italic"), fg="#0099cc")
    friday_edit_button.grid(row=0, column=4, padx=30, pady=(10,0))


    post_courses_to_timetable()

    global edit_container
    edit_container = LabelFrame(timetable_window, bd=0)
    edit_container.pack()


# Functia deschide fereastra de selectare a unei noi poze de profil. O data aleasa poza, functia va face update in
# tabela users, linia userului logat, coloana cale_imagine si va pune calea noii imagini.
def browse_profile_picture():
    global profile_picture
    #root.filename returneaza calea catre ceea ce selectez, initialdir ce se deschide, filetypes e ce tipuri pot accepta si trebuie sa respecte patternul ("png files", "*.png")
    root.filename = filedialog.askopenfilename(initialdir="C:/Users/lenovo/PycharmProjects/LicentaSasu/images", title="Select a file", filetypes=(("png files", "*.png"),("jpeg files","*.jpg"),("all files","*.*")))
    if root.filename != "":
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""UPDATE users SET
                   cale_imagine = :path
                   where oid = :oid""",
                       {'path': root.filename,
                        'oid': logged_original_id
                        })
        picture = Image.open(root.filename)
        picture = picture.resize((400, 350), Image.ANTIALIAS)
        profile_picture = ImageTk.PhotoImage(picture)
        profile_picture_label = Label(profile_window, image=profile_picture)
        profile_picture_label.image = profile_picture
        profile_picture_label.grid(row=1, column=2, rowspan=9, padx=(130, 0))

        conn.commit()
        conn.close()


# Functia afiseaza in profile_window poza de profil aferenta userului logat
def get_profile_picture_from_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    sql_querry = "SELECT cale_imagine FROM users WHERE oid=?"
    cursor.execute(sql_querry, (logged_original_id,))
    profile_picture_path = cursor.fetchone()
    picture = Image.open(profile_picture_path[0])
    picture = picture.resize((400, 350), Image.ANTIALIAS)
    profile_picture = ImageTk.PhotoImage(picture)

    profile_picture_label = Label(user_details_frame, image=profile_picture)
    profile_picture_label.image = profile_picture
    profile_picture_label.grid(row=1, column=2, rowspan=9, padx=(130, 0))

    conn.commit()
    conn.close()


def buttons_available(window, button):
    window.destroy()
    button.config(state=NORMAL)


def save_profile_changes(type):
    if change_entry_s.get() != change_entry_f.get():
        messagebox.showwarning("Atentie!", "Valorile nu coincid!")
    else:

        if type == "username":
            if len(change_entry_s.get()) >= 6 and len(change_entry_s.get()) <= 30:
                if user_does_exists(change_entry_s.get()) == "missing":
                    global logged_username
                    logged_username = change_entry_s.get()
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET username=:user_name WHERE oid = :id",
                           {'user_name': change_entry_s.get(),
                            'id': logged_original_id
                            })
                    conn.commit()
                    conn.close()
                    post_user_details()
                    messagebox.showinfo("Info!", "Usernameul a fost actualizat")
                    change_username_button.config(state=NORMAL)
                    make_changes_frame.destroy()
                else:
                    messagebox.showwarning("Atentie!", "Username deja folosit!")
            else:
                messagebox.showerror("Error!", "Username are prea putine sau prea multe caractere!")

        elif type == "email":
            if verify_email_format(change_entry_s.get()) == "emailformat":
                global logged_email
                logged_email = change_entry_s.get()
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET email=:em WHERE oid = :id",
                               {'em': change_entry_s.get(),
                                'id': logged_original_id
                                })
                conn.commit()
                conn.close()
                post_user_details()
                messagebox.showinfo("Info!", "Emailul a fost actualizat")
                change_email_button.config(state=NORMAL)
                make_changes_frame.destroy()
            else:
                messagebox.showwarning("Atentie!", "Emailul are formatul incorect!!")

        elif type == "parola":
            if len(change_entry_s.get()) > 8:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()

                new_user_pwd = change_entry_s.get().encode("utf-8")
                new_user_salt = bcrypt.gensalt()
                new_user_hashpwd = bcrypt.hashpw(new_user_pwd, new_user_salt)

                cursor.execute("UPDATE parole SET salt=:newsalt, hashpass=:newhashpass WHERE user_id = :oid",
                               {'newsalt': new_user_salt.decode(),
                                'newhashpass': new_user_hashpwd.decode(),
                                'oid': logged_original_id
                                })
                conn.commit()
                conn.close()
                messagebox.showinfo("Info!", "Parola a fost actualizata")
                change_pass_button.config(state=NORMAL)
                make_changes_frame.destroy()
            else:
                messagebox.showwarning("Atentie!", "Parola trebuie sa contina minim 8 caractere!")

        elif type == "prenume":
            if len(change_entry_s.get()) <= 15:
                global logged_first_name
                logged_first_name = change_entry_s.get()
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET prenume=:f_name WHERE oid = :id",
                               {'f_name': change_entry_s.get(),
                                'id': logged_original_id
                                })
                conn.commit()
                conn.close()
                post_user_details()
                messagebox.showinfo("Info!", "Prenumele a fost actualizat")
                make_changes_frame.destroy()
                change_firstname_button.config(state=NORMAL)
                post_top_bar_frame()
            else:
                messagebox.showwarning("Atentie!", "Prenumele contine prea multe caractere!")
        elif type == "nume":
            if len(change_entry_s.get()) <= 15:
                global logged_last_name
                logged_last_name = change_entry_s.get()
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET nume=:l_name WHERE oid = :id",
                               {'l_name': change_entry_s.get(),
                                'id': logged_original_id
                                })
                conn.commit()
                conn.close()
                post_user_details()
                messagebox.showinfo("Info!", "Numele a fost actualizat")
                change_lastname_button.config(state=NORMAL)
                make_changes_frame.destroy()
            else:
                messagebox.showwarning("Atentie!", "Numele contine prea multe caractere!")


def change_handler(type):
    for child in make_changes_frame.winfo_children():
        child.destroy()
    change_frame = LabelFrame(make_changes_frame, bd=0)
    change_frame.pack()

    global change_entry_s
    global change_entry_f
    global change_label_f
    global change_label_s
    change_label_f = Label(change_frame)
    change_label_f.grid(row=0, column=0, pady=(15,0))
    change_entry_f = Entry(change_frame, width=50)
    change_entry_f.grid(row=0, column=1, pady=(15,0))
    change_label_s = Label(change_frame)
    change_label_s.grid(row=1, column=0)
    change_entry_s = Entry(change_frame, width=50)
    change_entry_s.grid(row=1, column=1)

    save_changes_button = Button(change_frame, text="Salveaza", padx=50)
    save_changes_button.grid(row=2, column=0, columnspan=2, pady=(10,3))

    if type == "username":
        change_username_button.config(state=DISABLED)
        change_pass_button.config(state=NORMAL)
        change_email_button.config(state=NORMAL)
        change_firstname_button.config(state=NORMAL)
        change_lastname_button.config(state=NORMAL)
        change_label_f.config(text="Noul "+type+":")
        change_label_s.config(text="Confirmare "+type+":")
        save_changes_button.config(command=lambda: save_profile_changes("username"))

    elif type == "email":
        change_username_button.config(state=NORMAL)
        change_pass_button.config(state=NORMAL)
        change_firstname_button.config(state=NORMAL)
        change_lastname_button.config(state=NORMAL)
        change_email_button.config(state=DISABLED)
        change_label_f.config(text="Noul " + type + ":")
        change_label_s.config(text="Confirmare " + type + ":")
        save_changes_button.config(command=lambda: save_profile_changes("email"))

    elif type == "parola":
        change_username_button.config(state=NORMAL)
        change_pass_button.config(state=DISABLED)
        change_email_button.config(state=NORMAL)
        change_firstname_button.config(state=NORMAL)
        change_lastname_button.config(state=NORMAL)
        change_label_f.config(text="Noua "+type+":")
        change_label_s.config(text="Confirmare " + type + ":")
        change_entry_f.config(show="*")
        change_entry_s.config(show="*")
        save_changes_button.config(command=lambda: save_profile_changes("parola"))

    elif type == "prenume":
        change_firstname_button.config(state=DISABLED)
        change_pass_button.config(state=NORMAL)
        change_email_button.config(state=NORMAL)
        change_username_button.config(state=NORMAL)
        change_lastname_button.config(state=NORMAL)
        change_label_f.config(text="Noul " + type + ":")
        change_label_s.config(text="Confirmare " + type + ":")
        save_changes_button.config(command=lambda: save_profile_changes("prenume"))

    elif type == "nume":
        change_lastname_button.config(state=DISABLED)
        change_pass_button.config(state=NORMAL)
        change_email_button.config(state=NORMAL)
        change_username_button.config(state=NORMAL)
        change_firstname_button.config(state=NORMAL)
        change_label_f.config(text="Noul " + type + ":")
        change_label_s.config(text="Confirmare " + type + ":")
        save_changes_button.config(command=lambda: save_profile_changes("nume"))


def check_edit_pass(attempt_password):
    connpwd = sqlite3.connect('users.db')
    cursorpwd = connpwd.cursor()

    sql_query = """SELECT hashpass FROM parole WHERE user_id=?"""
    cursorpwd.execute(sql_query, (logged_original_id,))

    hashpass_database = cursorpwd.fetchone()
    connpwd.commit()
    connpwd.close()

    if bcrypt.checkpw(attempt_password.encode("utf-8"), hashpass_database[0].encode("utf-8")) == True:
        check_pass_frame.destroy()

        global change_options_frame
        change_options_frame = LabelFrame(edit_user_profile_frame, bd=0)
        change_options_frame.pack()

        global change_pass_button
        change_pass_button = Button(change_options_frame, text="Schimbare parola", bd=1, command= lambda: change_handler("parola"))
        change_pass_button.grid(row=0, column=0)

        global change_username_button
        change_username_button = Button(change_options_frame, text="Schimbare username", bd=1, command=lambda: change_handler("username"))
        change_username_button.grid(row=0, column=1)

        global change_email_button
        change_email_button = Button(change_options_frame, text="Schimbare email", bd=1, command=lambda: change_handler("email"))
        change_email_button.grid(row=0, column=2)

        global change_firstname_button
        change_firstname_button = Button(change_options_frame, text="Schimbare prenume", bd=1, command=lambda: change_handler("prenume"))
        change_firstname_button.grid(row=0, column=3)

        global change_lastname_button
        change_lastname_button = Button(change_options_frame, text="Schimbare nume", bd=1, command=lambda: change_handler("nume"))
        change_lastname_button.grid(row=0, column=4)

        global make_changes_frame
        make_changes_frame = LabelFrame(edit_user_profile_frame)
        make_changes_frame.pack(fill="both")

        global close_button
        close_button = Button(change_options_frame, text="X", command=lambda: close_edit("profil"), padx=10, bd=1,
                              font=("Helvetica", 10, "bold"))
        close_button.grid(row=0, column=5)
        close_button.bind("<Enter>", hover)
        close_button.bind("<Leave>", leave)
    else:
        messagebox.showerror("Eroare!", "Parola incorectă")


def hover(e):
    close_button['background'] = 'red'

def leave(e):
    close_button['background'] = 'SystemButtonFace'


def edit_user_profile():
    global edit_user_profile_frame
    edit_user_profile_frame = LabelFrame(profile_window)
    edit_user_profile_frame.pack(fill="both")
    edit_profile_button.config(state=DISABLED)

    global check_pass_frame
    check_pass_frame = LabelFrame(edit_user_profile_frame)
    check_pass_frame.pack(fill="both")



    close_button = Button(check_pass_frame, text="X", command=lambda: close_edit("profil"), padx=10, bd=1,
                          font=("Helvetica", 10, "bold"))
    close_button.pack(side=RIGHT)
    text_label = Label(check_pass_frame, text="Pentru a putea edita profilul, trebuie să introduceți parola contului", font=("Halvetica", 13))
    text_label.pack()

    pass_entry = Entry(check_pass_frame, width=50, show="*")
    pass_entry.pack()

    confirm_button = Button(check_pass_frame, text="Confirmă", command=lambda: check_edit_pass(pass_entry.get()))
    confirm_button.pack()


def post_user_details():
    for child in user_details.winfo_children():
        child.destroy()

    global user_details_frame
    user_details_frame = LabelFrame(user_details, bd=0)
    user_details_frame.pack()
    profile_welcome_frame = LabelFrame(user_details_frame, bd=0)
    profile_welcome_frame.grid(row=0, column=1, columnspan=2, padx=(0, 140))
    profile_welcome = Label(user_details_frame,
                            text="Bine ai venit pe profilul tau! \n Mai jos sunt informatiile aferente contului tau.",
                            font=("Helvetica", 11))
    profile_welcome.grid(row=0, column=0, columnspan=2, pady=20)

    first_name_profile_label = Label(user_details_frame, text="Prenume: " + logged_first_name, anchor="w")
    first_name_profile_label.grid(row=1, column=0, padx=(40, 0), sticky="W")
    last_name_profile_label = Label(user_details_frame, text="Nume: " + logged_last_name)
    last_name_profile_label.grid(row=2, column=0, padx=(40, 0), sticky="W")
    username_profile_label = Label(user_details_frame, text="Username: " + logged_username)
    username_profile_label.grid(row=3, column=0, padx=(40, 0), sticky="W")
    email_profile_label = Label(user_details_frame, text="Email: " + logged_email)
    email_profile_label.grid(row=4, column=0, padx=(40, 0), sticky="W")
    join_date_label = Label(user_details_frame, text="Data înregistrarii: " + logged_join_date)
    join_date_label.grid(row=5, column=0, padx=(40, 0), sticky="W")
    program_profile_label = Label(user_details_frame, text="Program de studiu: " + logged_program)
    program_profile_label.grid(row=6, column=0, padx=(40, 0), sticky="W")
    domain_profile_label = Label(user_details_frame, text="Domeniul: " + logged_profile)
    domain_profile_label.grid(row=7, column=0, padx=(40, 0), sticky="W")
    specialization_profile_label = Label(user_details_frame, text="Specializarea: " + logged_specialization)
    specialization_profile_label.grid(row=8, column=0, padx=(40, 0), sticky="W")
    year_profile_label = Label(user_details_frame, text="Anul: " + logged_year)
    year_profile_label.grid(row=9, column=0, padx=(40, 0), sticky="W")

    browse_profile_label = Label(user_details_frame, text="Adaugă o noua fotografie: ")
    browse_profile_label.grid(row=10, column=0, padx=(40, 0), sticky="W")
    browse_profile_button = Button(user_details_frame, text="Răsfoiește", padx=177, command=browse_profile_picture)
    browse_profile_button.grid(row=10, column=2, padx=(120, 0), sticky="E")

    get_profile_picture_from_database()

    global edit_profile_button
    edit_profile_button = Button(user_details_frame, text="Editează", padx=50, command=edit_user_profile)
    edit_profile_button.grid(row=11, column=0, columnspan=2)


# Functia deschide fereastra Profilul meu si afiseaza datele corespunzatoare userului logat
# Aceasta permite adaugarea unei noi imagini de profil, imaginea default este luata din baza de date
def show_user_profile():
    global profile_window
    profile_window= Toplevel()
    profile_window.title("Profilul meu")

    profile_button_menu.config(state=DISABLED)
    profile_window.protocol("WM_DELETE_WINDOW", lambda: buttons_available(profile_window, profile_button_menu))

    global user_details
    user_details = Label(profile_window)
    user_details.pack()

    post_user_details()



def select_from_calendar(course_name, course_button):
    course_button.config( fg="#0099cc")
    def select_exam_date():
        course_button.config(text=calendar_object.get_date(), fg="black")
        select_dateexam_button.config(state=DISABLED)
        calendar_frame.config(text="Calendar")

    calendar_frame.config(text="Examen "+course_name)

    select_dateexam_button.config(state=NORMAL, command=select_exam_date)
#
#
#
#         conn = sqlite3.connect('users.db')
#         cursor = conn.cursor()
#
#         sql_delete = "DELETE from restante WHERE user_id=?"
#         cursor.execute(sql_delete, (logged_original_id,))
#         for failed in commited_failed_exams:
#             sql_insert = """INSERT INTO restante(user_id, materie, data) VALUES(?, ?, ?)"""
#             com_insert =  logged_original_id, failed[0], failed[1]
#             cursor.execute(sql_insert, com_insert)
#
#         conn.commit()
#         conn.close()
#         messagebox.showinfo('Info', "Restantele au fost salvate")
def commit_exams_to_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    course_index = 0
    exams_list = []
    for course in current_courses:
        exams_list.append([course, course_date_buttons[course_index]['text']])
        course_index += 1

    for exam in exams_list:
        cursor.execute("UPDATE examene SET data=:date WHERE id_user = :oid and materie=:nume_materie",
                       {'date': exam[1],
                        'oid': logged_original_id,
                        'nume_materie':exam[0]
                        })

    failed_index = 0
    for failed in failed_list_from_database:
        failed[1] = failed_date_buttons[failed_index]['text']
        failed_index += 1

    for failed in failed_list_from_database:
        cursor.execute("UPDATE restante SET data=:date WHERE user_id = :oid and materie=:nume_materie",
                       {'date': failed[1],
                        'oid': logged_original_id,
                        'nume_materie':failed[0]
                        })
    conn.commit()
    conn.close()
    messagebox.showinfo("Info", "Datele examnelor au fost salvate")
    buttons_available(exams_window, exams_button_menu)


def get_exam_list_from_database(examen_type):
    if examen_type == "dateexamene":
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT materie, data FROM examene where id_user=?",(logged_original_id,))
        exams_database = cursor.fetchall()
        print(exams_database)
        conn.commit()
        conn.close()
        try:
            if exams_database[0][0] != None:
                exams_list = []
                for exams_course in exams_database:
                    exams_list.append([exams_course[0], exams_course[1]])
                print(exams_list)
                return exams_list
            else:
                print("reached")
                return []
        except:
            return []

    if examen_type == "daterestante":
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        sql_query = """SELECT materie, data FROM restante WHERE user_id = ?"""
        cursor.execute(sql_query, (logged_original_id,))
        failed_courses_database = cursor.fetchall()
        conn.commit()
        conn.close()
        try:
            if failed_courses_database[0] != "" and failed_courses_database[0] != None:
                failed_list = []
                for failed_course in failed_courses_database:
                    failed_list.append([failed_course[0], failed_course[1]])
                return failed_list
            else:
                return []
        except:
            return []


def initialize_exams_to_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    initial_dates = []
    for course in current_courses:
        initial_dates.append([course, "--/--/--"])

    for exam in initial_dates:
        sql_insert = """INSERT INTO examene(id_user, materie, data) VALUES(?, ?, ?)"""
        com_insert = logged_original_id, exam[0], exam[1]
        cursor.execute(sql_insert, com_insert)

    conn.commit()
    conn.close()


def show_exams():
    global exams_window
    exams_window = Toplevel()
    exams_window.title("Examenele")
    exams_welcome = Label(exams_window, text="Planificator Examene  ", font=("Times New Roman", 17, "italic"), fg="#0099cc")
    exams_welcome.pack(pady=(10,20))

    exams_button_menu.config(state=DISABLED)
    exams_window.protocol("WM_DELETE_WINDOW", lambda: buttons_available(exams_window, exams_button_menu))


    exams_frame = LabelFrame(exams_window)
    exams_frame.pack(side=LEFT, padx=(50,0), anchor=N)
    course_welcome = Label(exams_frame, text="Examene", font=("Times New Roman", 12, "italic"), fg="#0099cc")
    course_welcome.grid(row=1, column=0)
    exam_date_welcome = Label(exams_frame, text="Dată examen", font=("Times New Roman", 12, "italic"), fg="#0099cc")
    exam_date_welcome.grid(row=1, column=1)

    current_semester = get_current_semester()
    global current_courses
    current_courses = get_current_courses(logged_specialization, logged_year, 2)
    exams_list_from_database = get_exam_list_from_database("dateexamene")
    if exams_list_from_database == []:
        initialize_exams_to_database()
        exams_list_from_database = get_exam_list_from_database("dateexamene")

    global course_date_buttons
    course_date_buttons = []
    linie = 2
    for course in current_courses:
        course_text_label = Label(exams_frame, text=course)
        course_text_label.grid(row=linie, column=0, sticky="w", pady=5)

        linie += 1

    linie = 2
    for exam in exams_list_from_database:
        course_date_button = Button(exams_frame, text=exam[1], bd=1)
        course_date_button.config(command=lambda c=exam[0], button=course_date_button: select_from_calendar(c, button), width=20)
        course_date_button.grid(row=linie, column=1, sticky = "w", pady=5)

        course_date_buttons.append(course_date_button)
        linie += 1

    help_label = Label(exams_window, text="?", bd=0, font=("Times New Roman", 17, "bold"), fg="#0099cc")
    help_message_balon = Balloon(exams_window)
    help_message_balon.bind_widget(help_label, balloonmsg="Pentru a introduce sau a modifica datele examenelor, \napăsați pe butonul corespunzător examenului, selectați data examenului \nși apăsați butonul „Selectează”.")
    help_label.pack(side=RIGHT, anchor=SE, padx=(0,8))
    help_message_balon.subwidget('message')['bg'] = 'white'
    for sub in help_message_balon.winfo_children():
        sub.config(bg='white')

    global failed_list_from_database
    failed_list_from_database = get_exam_list_from_database("daterestante")

    if failed_list_from_database != []:
        failed_frame = LabelFrame(exams_window)
        failed_frame.pack(side=RIGHT, padx=(0,30), anchor=N)
        global failed_date_buttons
        failed_date_buttons = []
        failure_welcome = Label(failed_frame, text="Restanțe", font=("Times New Roman", 12, "italic"), fg="#0099cc")
        failure_welcome.grid(row=1, column=3)
        failure_date_welcome = Label(failed_frame, text="Dată restanță", font=("Times New Roman", 12, "italic"), fg="#0099cc")
        failure_date_welcome.grid(row=1, column=4)

        linie = 2
        col = 3
        for failed in failed_list_from_database:
            failed_text_label = Label(failed_frame, text=failed[0], padx=20)
            failed_text_label.grid(row=linie, column=col, sticky="w", pady=5)

            failed_date_button = Button(failed_frame, text=failed[1], bd=1)
            failed_date_button.config(command=lambda c=failed[0], button=failed_date_button: select_from_calendar(c, button), width=20)
            failed_date_button.grid(row=linie, column=col+1, sticky="w", pady=5)
            failed_date_buttons.append(failed_date_button)

            linie += 1
            if linie == 7:
                linie = 2
                col += 2

    global calendar_frame
    global calendar_object
    global select_dateexam_button
    calendar_frame = LabelFrame(exams_window, text="Examen", bd=0)
    calendar_frame.pack(padx=30)
    calendar_object = Calendar(calendar_frame, font="Arial 14",date_pattern='dd/mm/yy', selectmode="day", year=date.today().year, month=date.today().month, day=date.today().day)
    calendar_object.grid(row=0, column=0, columnspan=2)
    select_dateexam_button = Button(calendar_frame, text="Selectează", state=DISABLED, bd=1)
    select_dateexam_button.grid(row=1, column=0, columnspan=3)


    commit_exams = Button(exams_window, text="Salvează", command=commit_exams_to_database, bd=1, padx=100)
    commit_exams.pack(pady=(20,0))


def get_course_semester(course):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    sql_query = """SELECT semestru_materie from materii WHERE nume_materie = ? AND specializare_materie = ?"""
    cursor.execute(sql_query, (course, logged_specialization))
    semester_database = cursor.fetchall()

    conn.commit()
    conn.close()
    return int(semester_database[0][0])


def check_program_availability(exams, faileds, semester):
    all_failed_dates = True
    all_exams_dates = True

    for exam in exams:
        if exam[1] == "--/--/--":
            all_exams_dates = False
            break
    for failed in faileds:
        if failed[1] == "--/--/--":
            all_failed_dates = False
            break

    if all_failed_dates == True and all_exams_dates == True and user_has_hobbies() == True:
        return True
    else: return False


def initialize_hobbies_lists(session_length):
    global frar
    global rar
    global uneori
    global des
    global fdes
    global hobby_max_posted
    frar = []
    rar = []
    uneori = []
    des = []
    fdes = []
    hobby_max_posted = 0
    hobby_actual_freq = 0
    for hobby in hobbies_list:
        if hobby[1] == 1:
            frar.append([hobby[0], 0, int(session_length/11)])
            hobby_max_posted += int(session_length/11)
        elif hobby[1] == 2:
            rar.append([hobby[0], 0, int(session_length/8)])
            hobby_max_posted += int(session_length / 8)
        elif hobby[1] == 3:
            uneori.append([hobby[0], 0, int(session_length/6)])
            hobby_max_posted += int(session_length / 6)
        elif hobby[1] == 4:
            des.append([hobby[0], 0, int(session_length/4)])
            hobby_max_posted += int(session_length / 4)
        elif hobby[1] == 5:
            fdes.append([hobby[0], 0, int(session_length/2)])
            hobby_max_posted += int(session_length / 2)
    print(frar)
    print(rar)
    print(uneori)
    print(des)
    print(fdes)


def check_exam_day(date):
    exams = []
    checked = False
    for exam in exams_list:
        if date.day == exam[1].day and date.month == exam[1].month:
            exams.append(exam[0])
            checked = True
    if checked == True:
        return exams
    else: return None

import random
def recap_day(label):
    hobby_index = random.randint(0, 2)
    label_text = Label(label, text="Recitire cursuri "+ exams_list[hobby_index][0])
    label_text.pack()
#

def how_many_days_until_exam(date):
    for exam in exams_list:
        if exam[1].day > date.day and exam[1].month == date.month or exam[1].day < date.day and exam[1].month > date.month:
            delta = exam[1] - date
            return delta.days, exam[0]
    return 0, 0


def check_if_day_busy(date):
    days_till_next = how_many_days_until_exam(date)
    if days_till_next[0] == 1 or days_till_next[0] == 2:
        return True
    return False


def get_formulare(type):
    if type == "hobby":
        forms = ["E timpul pentru", "E vremea pentru", "Ar merge niște", "Poate"]
        rand = random.randint(0,3)
        return forms[rand]
    if type == "invatat":
        forms = ["Aprofundare", "Laboratoare", "Seminarii", "Rezolvare modele examene"]
        rand = random.randint(0, 3)
        return forms[rand]


def post_hobby(task_label):
    global hobby_max_posted
    global hobbies_posted
    number_of_tasks = 0
    for child in task_label.winfo_children():
        number_of_tasks += 1
    if number_of_tasks >= 3:
        return
    else:
        posted = False
        while posted == False and hobbies_posted != hobby_max_posted:
            list_index = random.randint(1, 5)
            if list_index == 1:
                operate_list = frar
            if list_index == 2:
                operate_list = rar
            if list_index == 3:
                operate_list = uneori
            if list_index == 4:
                operate_list = des
            if list_index == 5:
                operate_list = fdes
            if len(operate_list) != 0:
                hobby_index = random.randint(0, (len(operate_list)-1))
                if operate_list[hobby_index][1] < operate_list[hobby_index][2]:
                    formulare = get_formulare("hobby")
                    hobby_label = Label(task_label, text=formulare +" "+ operate_list[hobby_index][0].capitalize())
                    hobby_label.pack()
                    if list_index == 1:
                        frar[hobby_index][1] += 1
                    if list_index == 2:
                        rar[hobby_index][1] += 1
                    if list_index == 3:
                        uneori[hobby_index][1] += 1
                    if list_index == 4:
                        des[hobby_index][1] += 1
                    if list_index == 5:
                        fdes[hobby_index][1] += 1
                    posted = True

                    hobbies_posted += 1


def post_hobby_free(task_label):
    posted = False
    while posted == False:
        list_index = random.randint(1, 5)
        if list_index == 1:
            operate_list = frar
        if list_index == 2:
            operate_list = rar
        if list_index == 3:
            operate_list = uneori
        if list_index == 4:
            operate_list = des
        if list_index == 5:
            operate_list = fdes
        if len(operate_list) != 0:
            hobby_index = random.randint(0, (len(operate_list) - 1))
            formulare = get_formulare("hobby")
            hobby_label = Label(task_label, text=formulare + " " + operate_list[hobby_index][0].capitalize())
            hobby_label.pack()
            if list_index == 1:
                frar[hobby_index][1] += 1
            if list_index == 2:
                rar[hobby_index][1] += 1
            if list_index == 3:
                uneori[hobby_index][1] += 1
            if list_index == 4:
                des[hobby_index][1] += 1
            if list_index == 5:
                fdes[hobby_index][1] += 1
            posted = True


def post_busy(task_label):
    number_of_tasks = 0
    for child in task_label.winfo_children():
        number_of_tasks += 1
    if number_of_tasks >= 3:
        return
    else:
        label = Label(task_label, text="Test")
        label.pack()


def show_session_program():
    global exams_list
    exams_list = get_exam_list_from_database("dateexamene")
    failed_list = get_exam_list_from_database("daterestante")
    current_semester = get_current_semester()

    if failed_list != []:
        useless_items = []
        for failed in failed_list:
            if get_course_semester(failed[0]) != current_semester:
                useless_items.append(failed_list.index(failed))
        for useless in reversed(useless_items):
            failed_list.pop(useless)

    program_availability = check_program_availability(exams_list, failed_list, current_semester)

    if program_availability == False:
        messagebox.showinfo("Program sesiune!", "Pentru a accesa această funcționalitate trebuie să: \n -> introduceți toate datele examenelor, \n -> introduceți toate datele restanțelor semestrului curent, \n -> introduceți ocupațiile preferate.")
    else:
        for exam in exams_list:
            date_str = exam[1]
            date_time_obj = datetime.strptime(date_str, '%d/%m/%y')
            exam[1] = date_time_obj
        if failed_list != []:
            for failed in failed_list:
                date_str = failed[1]
                date_time_obj = datetime.strptime(date_str, '%d/%m/%y')
                failed[1] = date_time_obj
                exams_list.append(failed)
        failed_list.clear()

        exams_list = sorted(exams_list, key=lambda x: x[1])

        d = timedelta(days=5)
        session_first_date = exams_list[0][1] - d
        session_last_date = exams_list[-1][1]

        session_length = (session_last_date - session_first_date).days + 1

        if session_length > 30:
            messagebox.showinfo("Program sesiune!", "O sesiune poate dura maxim 30 de zile!")
            return
        if session_length < 15:
            messagebox.showinfo("Program sesiune!", "O sesiune dureaza minim 12 de zile!")
            return
        global hobbies_list
        hobbies_list = get_hobbies_list_from_database()
        hobbies_list = sorted(hobbies_list, key=lambda x: x[1])
        initialize_hobbies_lists(session_length)

        global session_program_window
        session_program_window = Toplevel()
        session_program_window.title("Program Sesiune")

        session_program_welcome = Label(session_program_window, text="Programul tău pentru sesiune, semestrul "+str(current_semester), font=("Times New Roman", 17, "italic"), fg="#0099cc")
        session_program_welcome.pack(pady=(10, 20))

        session_button_menu.config(state=DISABLED)
        session_program_window.protocol("WM_DELETE_WINDOW",
                                        lambda: buttons_available(session_program_window, session_button_menu))

        session_schedule_frame = LabelFrame(session_program_window)
        session_schedule_frame.pack(fill="both")
        # Lista de liste cu hobby si frecventa

        session_days_frame = LabelFrame(session_schedule_frame, bd=0)
        session_days_frame.pack()
        delta = timedelta(days=1)

        days_of_session = []
        free_days_session = []
        busy_days_session = []
        exams_day_session = []

        linie = 0
        col = 0
        today = date.today()
        session_day_index = 0
        dates = []
        tasks = []
        while session_first_date <= session_last_date:
            day_frame = LabelFrame(session_days_frame, text=session_first_date.strftime("%d-%m"))
            day_frame.grid(row=linie, column=col, padx=50, pady=30)
            days_of_session.append(day_frame)

            dates.append(session_first_date)

            day_tasks_label = Label(day_frame, width=32, height=5)
            day_tasks_label.pack()
            day_tasks_label.pack_propagate(False)
            tasks.append(day_tasks_label)
            if session_first_date.day == today.day and session_first_date.month == today.month:
                day_frame.config(fg="#0099cc")

            exam = check_exam_day(session_first_date)
            if exam != None:
                day_frame.config(fg="red")
                for lilexam in exam:
                    label = Label(day_tasks_label, text=lilexam)
                    label.pack()
                exams_day_session.append(day_frame)

            if session_day_index < 3:
                recap_day(day_tasks_label)

            col += 1
            if col == 5:
                linie += 1
                col =0
            session_day_index += 1
            session_first_date += delta

        session_day_index = len(days_of_session) - 1
        i = 0
        for day in reversed(days_of_session):
            exam = check_exam_day(dates[session_day_index])
            if exam != None:
                for lilexam in exam:
                    i = days_of_session.index(day)
                    formulare_invatat = get_formulare("invatat")
                    task_label = Label(tasks[i-1], text=formulare_invatat+" "+ lilexam)
                    task_label.pack()
                    formulare_invatat = get_formulare("invatat")
                    task_label1 = Label(tasks[i-2], text=formulare_invatat+" "+ lilexam)
                    task_label1.pack()
                    formulare_invatat = get_formulare("invatat")
                    task_label2 = Label(tasks[i-3], text=formulare_invatat+" "+ lilexam)
                    task_label2.pack()

            session_day_index -= 1

        session_day_index = 0
        for day in days_of_session:
            busy = check_if_day_busy(dates[session_day_index])
            if busy == True:
                busy_days_session.append(day)
            else:
                free_days_session.append(day)
            session_day_index += 1

        global hobbies_posted
        hobbies_posted = 0
        for free in free_days_session:
            post_hobby(tasks[days_of_session.index(free)])

        for day in days_of_session:
            task_label = tasks[days_of_session.index(day)]
            number_of_tasks = 0
            for child in task_label.winfo_children():
                number_of_tasks += 1
            if number_of_tasks == 0:
                post_hobby_free(task_label)


def check_program_semester_availability(monday_courses, tuesday_courses, wednesday_courses, thursday_courses, friday_courses):
    if len(monday_courses) + len(tuesday_courses) + len(wednesday_courses) + len(thursday_courses) + len(
            friday_courses) < 6:
        return False
    if len(monday_courses) + len(tuesday_courses) + len(wednesday_courses) + len(thursday_courses) + len(
            friday_courses) > 18:
        return False
    if user_has_hobbies() == False:
        return False


def select_courses_for_semester_program(day):
    print("orele de "+day+" sunt ")
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    sql_query = "SELECT tip_curs, nume_curs, ora_inceput, ora_sfarsit FROM oredecurs WHERE id_user=? and zi = ?"
    cursor.execute(sql_query, (logged_original_id,day))
    courses_from_database = cursor.fetchall()
    courses_of_day = []
    for course in courses_from_database:
        courses_of_day.append([course[0], course[1], course[2], course[3]])
    print(courses_of_day)
    return courses_of_day
    conn.close()

def show_semester_program():
    monday_courses = select_courses_for_semester_program("luni")
    tuesday_courses = select_courses_for_semester_program("marti")
    wednesday_courses = select_courses_for_semester_program("miercuri")
    thursday_courses = select_courses_for_semester_program("joi")
    friday_courses = select_courses_for_semester_program("vineri")

    program_availability = check_program_semester_availability(monday_courses, tuesday_courses, wednesday_courses, thursday_courses, friday_courses)

    if program_availability == False:
        messagebox.showinfo("Program semestru!",
                            "Pentru a accesa această funcționalitate trebuie să: \n -> introduceți orarul săptămânal: nu puteți avea în total mai puțin de 6 ore de curs sau mai mult de 18 \n -> introduceți ocupațiile preferate.")
    else:
        print("ok")



def post_top_bar_frame():
    top_bar_frame = LabelFrame(logged_in_frame, width=800, height=37, pady=0, bg="white")
    top_bar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    top_bar_frame.grid_propagate(False)
    top_image = Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/background/topbar4.png")

    top_background = ImageTk.PhotoImage(top_image)
    top_background_label = Label(top_bar_frame, image=top_background)
    top_background_label.image = top_background
    top_background_label.pack(fill="both", expand=1)

    welcome_text_label = Label(top_background_label, text="Salut, " + logged_first_name + "!", bg="white",  font=("Times New Roman", 16, "italic"), fg="#0099cc")
    welcome_text_label.pack(side=LEFT, padx=(10,0))
    logout_button = Button(top_background_label, text="Deconectare", command=logout_function)
    logout_button.pack(side=RIGHT)
    faq_button = Button(top_background_label, text="FAQ")
    faq_button.pack(side=RIGHT, padx=(0,5))


# Functia afiseaza logged_in_frame, ceea ce vede un utilizator dupa ce s-a logat cu succes.
def logged_in_function():
    global logged_in_frame
    logged_in_frame = LabelFrame(root,  width=1000, height=700, bd=0)
    logged_in_frame.place(in_=root, anchor="c", relx=.5, rely=.5)
    logged_user = username_login_input.get()
    global logged_original_id
    global logged_first_name
    global logged_last_name
    global logged_email
    global logged_username
    global logged_join_date
    global logged_year
    global logged_program
    global logged_profile
    global logged_specialization
    (logged_original_id, logged_first_name, logged_last_name, logged_username, logged_email, logged_join_date, logged_program, logged_profile, logged_specialization, logged_year) = querry_data_logged_user(logged_user)

    post_top_bar_frame()

    menu_frame = LabelFrame(logged_in_frame, bg="white", width=850, height=500)
    menu_frame.grid(row=1, column=0)

    global profile_button_menu
    global courses_button_menu
    global timetable_button_menu
    global hobbies_button_menu
    global schedule_button_menu
    global session_button_menu
    global reportcard_button_menu
    global exams_button_menu
    global notifications_button_menu
    profile_button_menu = Button(menu_frame, text="Profil", pady=83, padx=110, bd=0, command=show_user_profile)
    profile_button_menu.grid(row=0, column=0 , sticky="ew")
    courses_button_menu = Button(menu_frame, text="Materii", pady=83, padx=110, bd=0, command=show_current_courses)
    courses_button_menu.grid(row=0, column=1, sticky="ew", padx=10)
    timetable_button_menu = Button(menu_frame, text="Orar", pady=83, padx=110, bd=0, command=show_timetable)
    timetable_button_menu.grid(row=0, column=2, sticky="ew")
    hobbies_button_menu = Button(menu_frame, text="Hobbies", pady=83, padx=110, bd=0, command=show_users_hobbies)
    hobbies_button_menu.grid(row=1, column=0, sticky="ew", pady=10)
    schedule_button_menu = Button(menu_frame, text="Program", pady=83, padx=110, bd=0, command=show_semester_program)
    schedule_button_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
    session_button_menu = Button(menu_frame, text="Sesiune", pady=81, padx=90, bd=0, command=show_session_program)
    session_button_menu.grid(row=1, column=2, sticky="ew", pady=10)
    reportcard_button_menu = Button(menu_frame, text="Carnet", pady=83, padx=110, bd=0, command=show_report_card)
    reportcard_button_menu.grid(row=2, column=0 , sticky="ew")
    exams_button_menu = Button(menu_frame, text="Examene", pady=83, padx=110, bd=0, command=show_exams)
    exams_button_menu.grid(row=2, column=1, sticky="ew", padx=10)
    notifications_button_menu = Button(menu_frame, text="Notificari", pady=83, padx=110, bd=0)
    notifications_button_menu.grid(row=2, column=2, sticky="ew")


def modified(event):
    if profile_register_drop.get() == "Informatica":
        specialization_register_drop.config(value="Informatica")
        specialization_register_drop.current(0)
        year_register_drop.config(value=["I", "II", "III"])
        year_register_drop.current(0)
    if profile_register_drop.get() == "CTI":
        specialization_register_drop.config(value="CTI")
        specialization_register_drop.current(0)
        year_register_drop.config(value=["I", "II", "III", "IV"])
        year_register_drop.current(0)
    if profile_register_drop.get() == "Matematica":
        specialization_register_drop.config(value=["Matematica","Mate-Aplicata", "Mate-Info"])
        specialization_register_drop.current(0)
        year_register_drop.config(value=["I", "II", "III"])
        year_register_drop.current(0)

def spec_modified(event):
    if specialization_register_drop.get() == "Matematica":
        year_register_drop.config(value=["I","II","III"])
        year_register_drop.current(0)
    if specialization_register_drop.get() == "Mate-Aplicata" or specialization_register_drop.get() == "Mate-Info":
        year_register_drop.config(value=["II", "III"])
        year_register_drop.current(0)


def back_to_login_screen():
    register_frame.grid_forget()
    application_on()


# Functia permite utilizatorilor noi se inregistreze
# Nu vreau mai multe ferestre din register pe ecran TO BE DONE
def register_frame_show():
    root.bind('<Return>', register_database_function)
    login_frame.grid_forget()
    # Frame register e globala pentru a putea fi distrusa in alte functii precum back_to_login_screen sau cand inregistrarea a avut loc cu succes
    global register_frame
    register_frame = LabelFrame(root, padx=20, pady=20, bd=0)
    register_frame.place(in_=root, anchor="c", relx=.5, rely=.5)
    #Listele pentru Dropdowns
    study_programs =        [ "Licentă" ]
    study_profiles =        [ "Informatica", "Matematica", "CTI" ]
    study_specializations = [ "Informatica" ]
    study_years =           [ "I", "II", "III" ]

    # Label Texts pentru Register
    # Sunt globale pentru a le putea valida in registerDatabase (le schimb culoarea daca sunt necompletate)
    global first_name_register_label
    global last_name_register_label
    global username_register_label
    global password_register_label
    global email_register_label
    first_name_register_label = Label(register_frame, text="Prenume: ")
    first_name_register_label.grid(row=0, column=0, sticky=W)
    last_name_register_label = Label(register_frame, text="Nume: ")
    last_name_register_label.grid(row=1, column=0, sticky=W)
    username_register_label = Label(register_frame, text="Username: ")
    username_register_label.grid(row=2, column=0, sticky=W)
    password_register_label = Label(register_frame, text="Parola: ")
    password_register_label.grid(row=3, column=0, sticky=W)
    email_register_label = Label(register_frame, text="Email: ")
    email_register_label.grid(row=4, column=0, sticky=W)
    study_program_label = Label(register_frame, text="Programul de studiu: ")
    study_program_label.grid(row=5, column=0, pady=(20,0), sticky=W)
    profile_register_label = Label(register_frame, text="Domeniul: ")
    profile_register_label.grid(row=6, column=0, sticky=W, pady=(4,0))
    specialization_register_label = Label(register_frame, text="Specializare: ")
    specialization_register_label.grid(row=7, column=0, sticky=W, pady=(4,0))
    year_register_label = Label(register_frame, text="Anul de studiu: ")
    year_register_label.grid(row=8, column=0, sticky=W, pady=(4,0))


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
    global year_register_drop
    first_name_register_input = Entry(register_frame, width=30)
    first_name_register_input.grid(row=0, column=1, padx=15)
    last_name_register_input = Entry(register_frame, width=30)
    last_name_register_input.grid(row=1, column=1)
    username_register_input = Entry(register_frame, width=30)
    username_register_input.grid(row=2, column=1)
    password_register_input = Entry(register_frame, width=30, show="*")
    password_register_input.grid(row=3, column=1)
    email_register_input = Entry(register_frame, width=30)
    email_register_input.grid(row=4, column=1)

    program_register_drop = ttk.Combobox(register_frame, value=study_programs)
    program_register_drop.grid(row=5, column=1, pady=(20,0))
    program_register_drop.current(0)
    profile_register_drop = ttk.Combobox(register_frame, value=study_profiles)
    profile_register_drop.grid(row=6, column=1, pady=(4,0))
    profile_register_drop.current(0)
    profile_register_drop.bind('<<ComboboxSelected>>', modified)
    specialization_register_drop = ttk.Combobox(register_frame, value=study_specializations)
    specialization_register_drop.grid(row=7, column=1, pady=(4,0))
    specialization_register_drop.current(0)
    specialization_register_drop.bind('<<ComboboxSelected>>', spec_modified)
    year_register_drop = ttk.Combobox(register_frame, value=study_years)
    year_register_drop.grid(row=8, column=1, pady=(4,0))
    year_register_drop.current(0)

    submit_button_register = Button(register_frame, text="Înregistrare", command=register_database_function)
    submit_button_register.grid(row=10, column=0, columnspan=2, pady=10, ipadx=125)
    back_button_register = Button(register_frame, text="Inapoi", command=back_to_login_screen)
    back_button_register.grid(row=11, column=0, columnspan=2, ipadx=138)


# Functia afiseaza pe ecran aplicatia
def application_on():
    root.bind('<Return>', login_function)
    global login_frame

    login_frame = LabelFrame(root, padx=30, pady=80, bd=0)
    login_frame.place(in_=root, anchor="c", relx=.5, rely=.5)

    login_title = Label(login_frame, text="S+ Plan Program", font=("Times New Roman", 31, "italic"), fg="#0099cc", width=14)
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
    log_button_login = Button(login_frame, text="Autentificare", bd=1,command=login_function)
    log_button_login.grid(row=3, column=0, columnspan=2, ipadx=105, pady=5)
    register_button_login = Button(login_frame, text="Înregistrare", bd=1, command=register_frame_show)
    register_button_login.grid(row=4, column=0, columnspan=2, ipadx=110)


application_on()


root.mainloop()
