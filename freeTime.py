from tkinter import *
from datetime import date
import sqlite3
from tkinter import messagebox, ttk
from PIL import ImageTk, Image
import bcrypt
from tkinter import filedialog
import ast
from tkcalendar import *


root = Tk()
root.title("Schedule App")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("1400x800")
root.resizable(False, False)


# Functia verifica daca toate fieldurile din register card sunt completate
def verify_fields_completed():
    fields_ok = 1
    if first_name_register_input.get() == "" or last_name_register_input.get() == "" or username_register_input.get() == "" or password_register_input.get() == "" or email_register_input.get() == "":
        response = messagebox.showerror("Eroare!", "Nu ati completat toate campurile!")
        fields_ok = 0
    return fields_ok


# Functia verifica daca un user se afla sau nu in baza de date
def user_does_exists():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * from users")
    users_database = cursor.fetchall()
    exists = "missing"
    for user_database in users_database:
        username_test = user_database[2]
        if username_test == username_register_input.get():
            exists = "found"
            break
    conn.commit()
    conn.close()
    return exists


# Functia verifica daca emailul introdus in register window este valid pentru inregistrare
def verify_email_format():
    email_format = "unknownformat"
    if '@' in email_register_input.get() and '.' in email_register_input.get():
        email_format = "emailformat"
    return email_format


# Functia verifica daca toate datele introduse pentru inregistrare sunt valide si introduce datele in tabela users
# si parolele criptate in tabela parole
def register_database_function():
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
    elif user_does_exists() != "missing":
        messagebox.showerror("Error!", "Username deja folosit!")
    elif profile_register_drop.get() == "CTI" and specialization_register_drop.get() != "CTI":
        messagebox.showerror("Error!", "Domeniul CTI nu are aceasta specializare!")
    elif profile_register_drop.get() == "Informatica" and specialization_register_drop.get() != "Informatica":
        messagebox.showerror("Error!", "Domeniul Informatica nu are specializarea selectata!")
    elif profile_register_drop.get() == "Informatica" and specialization_register_drop.get() == "Informatica" and year_register_drop.get() == "IV":
        messagebox.showerror("Error!", "Domeniul Informatica nu are anul selectat!")
    elif profile_register_drop.get() == "Matematica" and (specialization_register_drop.get() == "Informatica" or specialization_register_drop.get() == "CTI"):
        messagebox.showerror("Error!", "Domeniul Matematica nu are specializarea selectata!")
    elif profile_register_drop.get() == "Matematica" and (specialization_register_drop.get() == "Mate-Info" or specialization_register_drop.get() == "Mate-Aplicata") and (year_register_drop.get() == "I" or year_register_drop.get() == "IV"):
        messagebox.showerror("Error!", "Domeniul Matematica nu are aceasta specializare la anul selectat!")
    elif profile_register_drop.get() == "Matematica" and specialization_register_drop.get() == "Matematica" and year_register_drop.get() == "IV":
        messagebox.showerror("Error!", "Domeniul Matematica nu are anul selectat!")
    elif verify_email_format() == "emailformat":
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

        cursor.execute("INSERT INTO parole VALUES (:user_id, :salt , :hashpass)",
                    {
                    'user_id': registered_user_original_id[0],
                    'salt': registered_user_salt.decode(),
                    'hashpass': registered_user_hashpwd.decode()
                    })

        cursor.execute("INSERT INTO orar VALUES (:id_user, :luni, :marti, :miercuri, :joi, :vineri)",
                       {
                           'id_user': registered_user_original_id[0],
                           'luni': None,
                           'marti': None,
                           'miercuri': None,
                           'joi': None,
                           'vineri': None,
                       })

        cursor.execute("INSERT INTO examene VALUES (:id_user, :lista_examene)",
                       {
                           'id_user': registered_user_original_id[0],
                           'lista_examene': None,
                           'lista_restante': None
                       })

        conn.commit()
        conn.close()
        response = messagebox.showinfo("Info!", "Inregistrarea a avut loc cu succes! ")
        if response == "ok":
            reg.destroy()
    else:
        reponse = messagebox.showerror("Error!", "Emailul are formatul incorect!!")


# Functia este handle pentru login button, daca username si parola sunt corecte, ne logam, altfel primim eroare.
def login_function(event=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    sql_query = """SELECT oid, username FROM users WHERE username = ?"""
    cursor.execute(sql_query, (username_login_input.get(),))
    username_database = cursor.fetchone()

    if username_database != None:
        connpwd = sqlite3.connect('users.db')
        cursorpwd = connpwd.cursor()

        sql_query =  """SELECT hashpass FROM parole WHERE user_id=?"""
        cursorpwd.execute(sql_query,(username_database[0],))
        hashpass_database = cursorpwd.fetchone()

        attempt_password = password_login_input.get()

        if bcrypt.checkpw(attempt_password.encode("utf-8"), hashpass_database[0].encode("utf-8")) == True:
            connpwd.commit()
            connpwd.close()
            login_frame.grid_forget()
            logged_in_function()
        else:
            response = messagebox.showerror("Error", "Datele introduse sunt invalide! Reincercati!")
    else:
        response = messagebox.showerror("Error", "Datele introduse sunt invalide1! Reincercati!")
    conn.commit()
    conn.close()


# Functia este handle pentru logout button, daca dorim sa ne delogam, ne intoarcem la login_frame_show iar celelalte
# ferestre deschise sunt distruse.
def logout_function():
    response = messagebox.askyesno("Disconnect", "Doriti sa va delogati?")
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


def get_current_failed_courses():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    sql_query = """SELECT lista_restante FROM examene WHERE id_user = ?"""
    cursor.execute(sql_query, (logged_original_id,))
    failed_courses_database = cursor.fetchone()
    conn.commit()
    conn.close()

    if failed_courses_database[0] != "" and failed_courses_database[0] != None:
        failed_courses_database = ast.literal_eval(failed_courses_database[0])
        for failed_course in failed_courses_database:
            failed_exams_list.append(failed_course)
        return failed_exams_list
    else:
        return []


def commit_failures_to_database():
    valid_failure = True
    dropdowns_values = []
    for dropdown in failed_exams_list_dropdowns:
        dropdowns_values.append(dropdown.get())

    error = ""
    for value in dropdowns_values:
        if value == "Sterge":
            error = "'Sterge' nu poate fi o restanta"
            valid_failure = False
            break

    if error == "":
        if len(set(dropdowns_values)) == len(dropdowns_values):
            for value in dropdowns_values:
                if value in failed_exams_list:
                    valid_failure = False
                    error = "Nu puteti avea mai mutle restante la aceeasi materie"
                    break;
        else:
            valid_failure = False
            error = "Nu puteti avea mai mutle restante la aceeasi materie"


    if valid_failure == True:
        for dropdown in failed_exams_list_dropdowns:
            failed_exams_list.append(dropdown.get())
        print(failed_exams_list)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("""UPDATE examene SET
                               lista_restante = :lista
                               WHERE id_user = :user_id""",
                       {'lista': str(failed_exams_list),
                        'user_id': logged_original_id
                        })

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
        semesters_to_show = (current_year * current_semester) - 1
    else:
        semesters_to_show = (current_year * 2 - 1) - 1

    past_courses = get_past_courses(semesters_to_show)
    past_courses.insert(0, "Sterge")

    failed_dropdown = ttk.Combobox(edit_failed_frame, value=past_courses)
    failed_dropdown.pack()
    failed_dropdown.current(0)
    failed_exams_list_dropdowns.append(failed_dropdown)


def delete_failed_course(vars):
    print(failed_exams_list)
    for var in reversed(vars):
        if var.get() == 1:
            failed_exams_list.pop(vars.index(var))
            failed_course_checkboxes[vars.index(var)].forget()
            failed_course_checkboxes.pop(vars.index(var))

    for var in reversed(vars):
        if var.get() == 1:
            vars.pop(vars.index(var))

    for dropdown in reversed(failed_exams_list_dropdowns):
        if dropdown.get() == "Sterge":
            dropdown.destroy()
            failed_exams_list_dropdowns.pop(failed_exams_list_dropdowns.index(dropdown))


def edit_failed_courses():
    global edit_failed_frame
    edit_failed_frame = LabelFrame(courses_window, text="Editare Restante")
    edit_failed_frame.pack(fill="both")
    edit_failed_button.config(state=DISABLED)
    global save_failed_button
    save_failed_button = Button(edit_failed_frame, text="Salveaza Restante", command=commit_failures_to_database)
    save_failed_button.pack()
    add_failed = Button(edit_failed_frame, text="Adauga restanta", command=add_failed_course)
    add_failed.pack()
    delete_failed = Button(edit_failed_frame, text="Sterge restante", command=lambda: delete_failed_course(vars))
    delete_failed.pack()

    global failed_course_checkboxes
    failed_course_checkboxes = []
    vars = []
    if failed_exams_list != []:
        for failed_course in failed_exams_list:
            var = IntVar()
            vars.append(var)
            failed_course_checkbox = Checkbutton(edit_failed_frame, text=failed_course, variable=var)
            print(var.get())
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
    edit_failed_button = Button(failed_frame, text="Editeaza Restante", command=edit_failed_courses)

    failed_exams_list = get_current_failed_courses()
    print(failed_exams_list)
    if failed_exams_list != []:
        for failed_course in failed_exams_list:
            failed_course_label = Label(failed_frame, text=failed_course)
            failed_course_label.pack()
        edit_failed_button.pack()
    else:
        no_failure_label = Label(failed_frame, text="Nu ai restante!")
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
    if string_year == "III": return 3
    if string_year == "II": return 2
    if string_year == "I": return 1


# Functia e folosita in querry_grades pentru a ne permite sa apelam querry_courses dupa an(string) / semestru
def get_year_as_string(int_year):
    if int_year == 1: return "I"
    if int_year == 2: return "II"
    if int_year == 3: return "III"


# Functia intoarce 'semesters to show' semestre incepand din semestrul 1 anul 1
def get_past_courses(semesters_to_show):
    shown_semester = 1
    cursor_semester = 1
    cursor_year = 1
    courses_done = []

    if logged_specialization == "Mate-Info" or logged_specialization == "Mate-Aplicata":
        while shown_semester <= 2:
            cursor_year_string = get_year_as_string(cursor_year)
            courses = get_current_courses("Matematica", cursor_year_string, cursor_semester)
            for course in courses:
                courses_done.append(course)
            shown_semester += 1
            cursor_semester += 1

        cursor_year = 2
        cursor_semester = 1

    while shown_semester != semesters_to_show + 1:
        cursor_year_string = get_year_as_string(cursor_year)
        courses = get_current_courses(logged_specialization, cursor_year_string, cursor_semester)

        for course in courses:
            courses_done.append(course)

        cursor_semester += 1
        if cursor_semester == 3:
            cursor_year += 1
            cursor_semester = 1
        shown_semester += 1

    return courses_done


# Functia furnizeaza un vector de note care corespunde vectorului user past courses
def get_grades_from_database(user_past_courses):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    grades = []

    for i in range(len(user_past_courses)):
        sql_query = """SELECT nota FROM note WHERE id_user = ? AND nume_materie = ?"""
        cursor.execute(sql_query, (logged_original_id, user_past_courses[i]))
        grade_database = cursor.fetchone()
        grades.append(grade_database)

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
        grades_window.destroy()


# Functia afiseaza pe grades_window materiile si notele pe care le-am obtinut, din trecut pana in prezent.
def show_report_card():
    global grades_window
    grades_window = Toplevel()
    grades_window.title("Carnet de note")
    grades_window.geometry("450x800")

    current_semester = get_current_semester() # Aflam semestrul in care suntem
    current_year = get_year_as_int(logged_year) # Luam anul in care suntem ca int

    # Aflam cate semestre trebuie sa postam
    if current_semester == 2:
        semesters_to_show = current_year * current_semester
    else:
        semesters_to_show = current_year * 2 - 1

    user_past_courses = get_past_courses(semesters_to_show) # Luam toate cursurile din trecut + cele din prezent
    user_grades = get_grades_from_database(user_past_courses) # Luam notele la materiile din trecut + cele din prezent unele vor fi None
    note = ["-", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    course_dropdowns = [] # Vectorul in care tinem casutele de tip dropdown si valorile acestora. Casutele corespund materiei i din vecctorul user_past_courses

    linie = 0 # Linia ne ajuta la postarea elementelor in fereastra
    for i in range(0, len(user_past_courses)):  # Pentru fiecare curs, il postam in stanga si nota acestuia in dreapta
        course_text_label = Label(grades_window, text=user_past_courses[i])
        course_text_label.grid(row=linie, column=0, sticky="w")

        course_dropdown = ttk.Combobox(grades_window, value=note)
        if  user_grades[i] == None:
            course_dropdown.current(0)
        else:
            course_dropdown.current(user_grades[i][0])
        course_dropdown.grid(row=linie, column=1)
        course_dropdowns.append(course_dropdown)
        linie += 1

    save_changes = Button(grades_window, text="Salveaza", command=lambda: commit_grades_database(course_dropdowns, user_past_courses))
    save_changes.grid(row=linie+1, column=0, columnspan=2, pady=20)


# Functia deselecteaza un hobby: ii reseteaza dimensiunile si padding normal + il scoate din lista de hobby-uri selectate
def deselect_hobby(i):
    hobby_images_buttons[i].config(width = 200, height= 150, command=lambda: select_hobby(i))
    hobby_images_buttons[i].grid(padx=0, pady=0)
    selected_hobbies.remove(i)


# Functia selecteaza un hobby: ii schima dimensiunile si paddingul + il adauga in lista de hobby-uri selectate
def select_hobby(i):
    if len(selected_hobbies) <= 5:
        selected_hobbies.append(i)
        hobby_images_buttons[i].config(width=150, height=100, command=lambda: deselect_hobby(i))
        hobby_images_buttons[i].grid(padx=25, pady=25)
    else:
        messagebox.showinfo("Info", "Ați selectat deja 6 ocupații!")


# Adaug hobby-urile userului in baza de date: Daca e prima data cand userul introduce hobby-uri, atunci inserez
# Daca userul isi editeaza hobby-urile, atunci fac update
def commit_hobbies_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id_user FROM usershobbies")
    users = cursor.fetchall()

    user_has_hobbies = 0
    for user in users:
        if user[0] == logged_original_id:
            user_has_hobbies = 1

    if len(selected_hobbies) == 6:
        if user_has_hobbies == 1:
            cursor.execute("""UPDATE usershobbies SET
                        index_1 = :first,
                        index_2 = :second,
                        index_3 = :third,
                        index_4 = :fourth,
                        index_5 = :fiveth,
                        index_6 = :sixth
                        where id_user = :user_id""",
                           {'first': selected_hobbies[0],
                            'second':selected_hobbies[1],
                            'third': selected_hobbies[2],
                            'fourth': selected_hobbies[3],
                            'fiveth': selected_hobbies[4],
                            'sixth': selected_hobbies[5],
                            'user_id': logged_original_id
                            })
            response = messagebox.showinfo("Info", "Modificările au fost salvate!")

            if response == "ok":
                hobbies_edit_window.destroy()
            conn.commit()
            conn.close()
        else:
            cursor.execute("INSERT INTO usershobbies VALUES (:id_user, :index_1, :index_2, :index_3, :index_4, :index_5, :index_6)",
                           {
                               'id_user': logged_original_id,
                               'index_1': selected_hobbies[0],
                               'index_2': selected_hobbies[1],
                               'index_3': selected_hobbies[2],
                               'index_4': selected_hobbies[3],
                               'index_5': selected_hobbies[4],
                               'index_6': selected_hobbies[5],
                           })
            response = messagebox.showinfo("Info", "Modificările au fost salvate!")

            if response == "ok":
                hobbies_edit_window.destroy()
            conn.commit()
            conn.close()

    else:
        messagebox.showwarning("Avertisment", "Trebuie să alegeți 6 ocupații.")


# Functia intoarce hobbyurile unui user, folosita pentru a afisa hobbyurile care au fost selectate in trecut
def get_selected_hobbies_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    selected_hobbies_from_database = []
    sql_query = """SELECT index_1, index_2, index_3, index_4, index_5, index_6 FROM usershobbies WHERE id_user = ?"""
    cursor.execute(sql_query, (logged_original_id,))
    selected_hobbies_from_database_tuple = cursor.fetchone()

    if selected_hobbies_from_database_tuple != None:
        for hobby in selected_hobbies_from_database_tuple:
            selected_hobbies_from_database.append(hobby)

    conn.commit()
    conn.close()
    return selected_hobbies_from_database


# Functia permite userului sa-si aleaga alte hobby-uri dintr-o matrice de 3 x 7. Noile hobby-uri vor fi salvate
# in baza de date cu ajutorul butonului save_hobbies care apeleaza commit_hobbies_database()
def edit_hobbies():
    global hobbies_edit_window
    hobbies_edit_window = Toplevel()
    hobbies_edit_window.title("Noile ocupațiile")
    pick_hobbies = Label(hobbies_edit_window, text="Alege 6 ocupatii preferate!", font=("Helvetica", 12))
    pick_hobbies.grid(row=0, column=3)

    global hobby_images_buttons
    hobby_images_buttons = []

    for i in range(21):
        image = Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/" + str(i) + ".jpg")
        image = image.resize((200, 150), Image.ANTIALIAS)
        hobby_img_to_post = ImageTk.PhotoImage(image)

        hobby_images_buttons.append(i)
        if i not in selected_hobbies:
            hobby_images_buttons[i] = Button(hobbies_edit_window, image=hobby_img_to_post,
                                             command=lambda index=i: select_hobby(index))
        else:
            hobby_images_buttons[i] = Button(hobbies_edit_window, image=hobby_img_to_post,
                                             command=lambda index=i: deselect_hobby(index), width=150, height=100)

        hobby_images_buttons[i].image = (hobby_img_to_post)

    r = 1
    c = 0
    for but in hobby_images_buttons:
        if c == 7:
            r += 1
            c = 0
        if hobby_images_buttons.index(but) in selected_hobbies:
            but.grid(row=r, column=c, padx=25, pady=25)
        else:
            but.grid(row=r, column=c)
        c += 1

    save_hobbies = Button(hobbies_edit_window, text="Salveaza", command=commit_hobbies_database)
    save_hobbies.grid(row=5, column=2, columnspan=2)


# Functia afiseaza in hobbies_window, hobby-urile selectate anterior de catre user
def post_users_hobbies():
    col = 0
    for i in selected_hobbies:
        image = Image.open("C:/Users/lenovo/PycharmProjects/LicentaSasu/images/" + str(i) + ".jpg")
        image = image.resize((200, 150), Image.ANTIALIAS)
        hobby_img_to_post = ImageTk.PhotoImage(image)

        hobby_img_label = Label(hobbies_window, image=hobby_img_to_post)
        hobby_img_label.image = hobby_img_to_post
        hobby_img_label.grid(row=1, column=col)
        col += 1


# Functia verifica prima data daca userul are hobby-uri in tabela usershobbies, daca da atunci le afiseaza si permite
# editarea acestora, daca nu, functia afiseaza direct fereastra de selectare a hobby-urilor
# hobbyurile selectate sunt afisate prin intermediul functiei post_users_hobbies
def show_users_hobbies():
    global hobbies_window
    hobbies_window = Toplevel()
    hobbies_window.title("Ocupațiile mele")

    global selected_hobbies
    selected_hobbies = get_selected_hobbies_database()
    if len(selected_hobbies) == 0:
        edit_hobbies()
        hobbies_window.destroy()
    else:
        your_hobbies = Label(hobbies_window, text="Ocupații preferate:")
        your_hobbies.grid(row=0, column=0)

        post_users_hobbies()

        edit_button = Button(hobbies_window, text="Editeaza", command=edit_hobbies)
        edit_button.grid(row=2, column=2, columnspan=2)
        refresh_button_hobbies = Button(hobbies_window, text="Refresh", command=post_users_hobbies)
        refresh_button_hobbies.grid(row=2, column=3)


def check_if_hours_valid(hours_start, hours_over):
    for hour_s, hour_o in zip(hours_start, hours_over):
        if (hour_s >= hour_o):
            error_message = "Ora de inceput a unei ore de curs nu poate fi mai mare decat cea de sfarsit!"
            return False, error_message

    if len(hours_start) > len(set(hours_start)) or len(hours_over) > len(set(hours_over)):
        error_message = "Nu puteti incepe sau sfarsi doua ore de curs in acelasi timp!"
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

        courses_list_for_day = sorted(courses_list_for_day, key = lambda x: x[2]) # Sortam lista de liste dupa ora de start a orei de curs
        cursor.execute("UPDATE orar SET "+Day+"=:orar WHERE id_user = :oid",
                    {'orar': str(courses_list_for_day),
                    'oid': logged_original_id
                    })
        messagebox.showinfo("Info", "Modificarile au fost salvate")
        edit_day_window.destroy()

        conn.commit()
        conn.close()
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

        course_type_label = Label(edit_day_window, text="Tipul orei")
        course_type_label.grid(row=1, column=0, padx=(20, 20), pady=(30, 10))
        course_name_label = Label(edit_day_window, text="Numele orei")
        course_name_label.grid(row=1, column=1, padx=(20, 20), pady=(30, 10))
        course_hour_start_label = Label(edit_day_window, text="Ora inceput")
        course_hour_start_label.grid(row=1, column=2, padx=(20, 20), pady=(30, 10))
        course_hour_over_label = Label(edit_day_window, text="Ora sfarsit")
        course_hour_over_label.grid(row=1, column=3, padx=(20, 20), pady=(30, 10))

        for i in range(0,number_of_courses_for_day):
            course_type_drop = ttk.Combobox(edit_day_window, value=course_type_list)
            course_type_drop.grid(row=i+2, column=0, pady=(0, 20), padx=(20, 20))
            course_type_drop.current(0)

            course_name_drop = ttk.Combobox(edit_day_window, value=courses_list)
            course_name_drop.grid(row=i+2, column=1, pady=(0, 20), padx=(20, 20))
            course_name_drop.current(0)

            hour_start_drop = ttk.Combobox(edit_day_window, value=hours_start)
            hour_start_drop.grid(row=i+2, column=2, pady=(0, 20), padx=(20, 20))
            hour_start_drop.current(0)

            hour_over_drop = ttk.Combobox(edit_day_window, value=hours_over)
            hour_over_drop.grid(row=i+2, column=3, pady=(0, 20), padx=(20, 20))
            hour_over_drop.current(0)


            courses_drop_list_for_day.append([course_type_drop, course_name_drop, hour_start_drop, hour_over_drop])

    else:
        how_many_courses.config(fg="red")


def edit_courses_day(Day):
    global edit_day_window
    edit_day_window = Toplevel()
    edit_day_window.title("Editare "+Day)

    global save_course_button
    save_course_button = Button(edit_day_window, text="Salveaza", state=DISABLED, command=lambda: commit_courses_of_day(Day), padx=70)
    save_course_button.grid(row=0, column=3, padx=(20,20))

    edit_day_label = Label(edit_day_window, text="Editeaza materiile de "+Day)
    edit_day_label.grid(row=0, column=1, columnspan=2)

    # how many si this many sunt globale pentru a putea fi sterse in functia add courses for edit
    global how_many_courses
    how_many_courses = Label(edit_day_window, text="Cate materii veti "+Day+"?")
    how_many_courses.grid(row=1, column=0, padx=(20,20))

    global this_many_courses
    this_many_courses = Entry(edit_day_window, width=60)
    this_many_courses.grid(row=1, column=1)

    global add_course_button
    add_course_button = Button(edit_day_window, text="Adauga in orarul de " + Day, command=add_course_for_edit)
    add_course_button.grid(row=0, column=0, padx=(20,20))


def select_courses_for_timetable(day_frame, day):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    linie = 0

    sql_query = "SELECT "+day+" FROM orar WHERE id_user=?"
    cursor.execute(sql_query, (logged_original_id,))
    courses_from_database = cursor.fetchone()
    courses_of_day = courses_from_database[0]
    if courses_of_day == None:
        courses_not_found = Label(day_frame, text="Nu ati introdus valorile \n pentru ziua "+day.capitalize())
        courses_not_found.grid(row=0, column=0)
    else:
        courses_of_day = ast.literal_eval(courses_of_day)
        for course in courses_of_day:
            course_timetable_label = Label(day_frame, text=course[2] + "-" + course[3] + " " + course[0] + " " + course[1])
            course_timetable_label.grid(row=linie, column=0)
            linie += 1

    conn.close()
    return


def post_courses_to_timetable():
    select_courses_for_timetable(monday_frame, "luni")
    select_courses_for_timetable(tuesday_frame, "marti")
    select_courses_for_timetable(wednesday_frame, "miercuri")
    select_courses_for_timetable(thursday_frame, "joi")
    select_courses_for_timetable(friday_frame, "vineri")


def destroy_courses_from_timetable():
    for monday_course in monday_frame.winfo_children():
        monday_course.destroy()
    for tuesday_course in tuesday_frame.winfo_children():
        tuesday_course.destroy()
    for wednesday_course in wednesday_frame.winfo_children():
        wednesday_course.destroy()
    for thursday_course in thursday_frame.winfo_children():
        thursday_course.destroy()
    for friday_course in friday_frame.winfo_children():
        friday_course.destroy()

    post_courses_to_timetable()


def show_timetable():
    global timetable_window
    timetable_window = Toplevel()
    timetable_window.title("Editarea orarului meu")

    monday_edit_button = Button(timetable_window, text="Luni", command=lambda: edit_courses_day("Luni"), padx=50)
    monday_edit_button.grid(row=0, column=0, padx=30)
    tuesday_edit_button = Button(timetable_window, text="Marti", command=lambda: edit_courses_day("Marti"), padx=48)
    tuesday_edit_button.grid(row=0, column=1, padx=30)
    wednesday_edit_button = Button(timetable_window, text="Miercuri", command=lambda: edit_courses_day("Miercuri"), padx=40)
    wednesday_edit_button.grid(row=0, column=2, padx=30)
    thursday_edit_button = Button(timetable_window, text="Joi", command=lambda: edit_courses_day("Joi"), padx=54)
    thursday_edit_button.grid(row=0, column=3, padx=30)
    friday_edit_button = Button(timetable_window, text="Vineri", command=lambda: edit_courses_day("Vineri"), padx=46)
    friday_edit_button.grid(row=0, column=4, padx=30)

    global monday_frame
    global tuesday_frame
    global wednesday_frame
    global thursday_frame
    global friday_frame
    monday_frame = LabelFrame(timetable_window, text="Luni", font=("Halvetica", 20), padx=5, pady=5)
    monday_frame.grid(row=1, column=0, pady=(30,20), sticky="n")  # padding outside frame
    tuesday_frame = LabelFrame(timetable_window, text="Marti", font=("Halvetica", 20), padx=5, pady=5)
    tuesday_frame.grid(row=1, column=1, pady=(30, 20), sticky="n")
    wednesday_frame = LabelFrame(timetable_window, text="Miercuri", font=("Halvetica", 20), padx=5, pady=5)
    wednesday_frame.grid(row=1, column=2, pady=(30, 20), sticky="n")
    thursday_frame = LabelFrame(timetable_window, text="Joi", font=("Halvetica", 20), padx=5, pady=5)
    thursday_frame.grid(row=1, column=3, pady=(30, 20), sticky="n")
    friday_frame = LabelFrame(timetable_window, text="Vineri", font=("Halvetica", 20), padx=5, pady=5)
    friday_frame.grid(row=1, column=4, pady=(30, 20), sticky="n")
    post_courses_to_timetable()

    refresh_timetable_button = Button(timetable_window, text="Refresh", command=destroy_courses_from_timetable)
    refresh_timetable_button.grid(row=2, column=4, sticky="se")


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

    profile_picture_label = Label(profile_window, image=profile_picture)
    profile_picture_label.image = profile_picture
    profile_picture_label.grid(row=1, column=2, rowspan=9, padx=(130, 0))

    conn.commit()
    conn.close()


# Functia deschide fereastra Profilul meu si afiseaza datele corespunzatoare userului logat
# Aceasta permite adaugarea unei noi imagini de profil, imaginea default este luata din baza de date
def show_profile():
    global profile_window
    profile_window= Toplevel()
    profile_window.title("Profilul meu")
    profile_window.geometry("800x500")
    profile_window.resizable(False, False)

    profile_welcome_frame = LabelFrame(profile_window, bd=0)
    profile_welcome_frame.grid(row=0, column=1, columnspan=2, padx=(0, 140))
    profile_welcome = Label(profile_welcome_frame, text="Bine ai venit pe profilul tau! \n Mai jos sunt informatiile aferente contului tau.", font=("Helvetica", 11))
    profile_welcome.grid(row=0, column=0, columnspan=2, pady=20)

    first_name_profile_label = Label(profile_window, text="Prenume: " + logged_first_name, anchor="w")
    first_name_profile_label.grid(row=1, column=0, padx=(40,0))
    last_name_profile_label = Label(profile_window, text="Nume: " + logged_last_name)
    last_name_profile_label.grid(row=2, column=0, padx=(40,0))
    username_profile_label = Label(profile_window, text="Username: "+ logged_username)
    username_profile_label.grid(row=3, column=0, padx=(40,0))
    email_profile_label = Label(profile_window, text="Email: "+ logged_email)
    email_profile_label.grid(row=4, column=0, padx=(40,0))
    join_date_label = Label(profile_window, text="Data inregistrarii: "+ logged_join_date)
    join_date_label.grid(row=5, column=0, padx=(40,0))
    program_profile_label = Label(profile_window, text="Program de studiu: "+ logged_program)
    program_profile_label.grid(row=6, column=0, padx=(40,0))
    domain_profile_label = Label(profile_window, text="Domeniul: "+ logged_profile)
    domain_profile_label.grid(row=7, column=0, padx=(40,0))
    specialization_profile_label = Label(profile_window, text="Specializarea: "+ logged_specialization)
    specialization_profile_label.grid(row=8, column=0, padx=(40,0))
    year_profile_label = Label(profile_window, text="Anul: "+ logged_year)
    year_profile_label.grid(row=9, column=0, padx=(40,0))

    browse_profile_label = Label(profile_window, text="Adauga o noua fotografie: ")
    browse_profile_label.grid(row=10, column=0)
    browse_profile_button = Button(profile_window, text="Browse", padx=177, command=browse_profile_picture)
    browse_profile_button.grid(row=10, column=2, padx=(130, 0))

    get_profile_picture_from_database()


def show_calendar(course_name, course_button):
    def select_exam_date():
        course_button.config(text=calendar_object.get_date())
        select_dateexam_button.config(state=DISABLED)
        calendar_frame.config(text="Calendar")

    calendar_frame.config(text="Examen "+course_name)

    select_dateexam_button.config(state=NORMAL, command=select_exam_date)


def commit_exams_to_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    course_index = 0
    exams_list = []
    for course in current_courses:
        exams_list.append([course, course_date_buttons[course_index]['text']])
        course_index += 1
    print(exams_list)
    cursor.execute("UPDATE examene SET lista_examene=:exams WHERE id_user = :oid",
                   {'exams': str(exams_list),
                    'oid': logged_original_id
                    })
    conn.commit()
    conn.close()
    messagebox.showinfo("Info", "Datele examnelor au fost salvate")
    exams_window.destroy()


def get_exam_list_from_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT lista_examene FROM examene where id_user=?",(logged_original_id,))
    exams = cursor.fetchone()

    conn.commit()
    conn.close()

    return exams[0]


def show_exams():
    global exams_window
    exams_window = Toplevel()
    exams_window.title("Examenele")
    exams_welcome = Label(exams_window, text="Aici se reasesc datele examenelor: ")
    exams_welcome.grid(row=0, column=0)

    course_welcome = Label(exams_window, text="Examene")
    course_welcome.grid(row=1, column=0)
    exam_date_welcome = Label(exams_window, text="Data examen")
    exam_date_welcome.grid(row=1, column=1)
    failure_welcome = Label(exams_window, text="Restante")
    failure_welcome.grid(row=1, column=3)
    failure_date_welcome = Label(exams_window, text="Data restanta")
    failure_date_welcome.grid(row=1, column=4)

    current_semester = get_current_semester()
    global current_courses
    current_courses = get_current_courses(logged_specialization, logged_year, 2)

    exams_list_from_database = get_exam_list_from_database()
    exams_list_from_database = ast.literal_eval(exams_list_from_database)
    print(exams_list_from_database)

    global course_date_buttons
    course_date_buttons = []
    linie = 2
    for course in current_courses:
        course_text_label = Label(exams_window, text=course)
        course_text_label.grid(row=linie, column=0, sticky="w")

        linie += 1

    linie = 2
    for exam in exams_list_from_database:
        course_date_button = Button(exams_window, text=exam[1])
        course_date_button.config(command=lambda c=exam[0], button=course_date_button: show_calendar(c, button), padx=20)
        course_date_button.grid(row=linie, column=1, sticky = "w")

        course_date_buttons.append(course_date_button)
        linie += 1

    global calendar_frame
    global calendar_object
    global select_dateexam_button
    calendar_frame = LabelFrame(exams_window, text="Examen")
    calendar_frame.grid(row=1, column=2, rowspan=6, padx=(30,20))
    calendar_object = Calendar(calendar_frame, font="Arial 14", selectmode="day", year=date.today().year, month=date.today().month, day=date.today().day)
    calendar_object.grid(row=0, column=0, columnspan=2)
    select_dateexam_button = Button(calendar_frame, text="Selecteaza", state=DISABLED)
    select_dateexam_button.grid(row=1, column=1)

    commit_exams = Button(exams_window, text="Salveaza", command=commit_exams_to_database)
    commit_exams.grid(row=linie, column=0)



# Functia afiseaza logged_in_frame, ceea ce vede un utilizator dupa ce s-a logat cu succes.
def logged_in_function():
    global logged_in_frame
    logged_in_frame = LabelFrame(root, bg="white",  width=1000, height=700, bd=0, padx=60, pady=30)
    logged_in_frame.place(relx=.15, rely=.1)
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

    #Pentru a manipula Welcome label text si logout button, schimb valorile din padx din gridurile lor
    top_bar_frame = LabelFrame(logged_in_frame, width=850, height=100, bg="white")
    top_bar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    welcome_label = Label(top_bar_frame, text="Salut, " + logged_first_name + "!", bg="white", font=("Helvetica", 15))
    welcome_label.grid(row=0, column=0, padx=(10,170))
    logout_button = Button(top_bar_frame, text="Log off", command=logout_function)
    logout_button.grid(row=0, column=2, sticky="ew")
    faq_button = Button(top_bar_frame, text="FAQ")
    faq_button.grid(row=0, column=1, sticky="ew", padx=(440, 0))

    menu_frame = LabelFrame(logged_in_frame, bg="white", width=850, height=500)
    menu_frame.grid(row=1, column=0)

    profile_button_menu = Button(menu_frame, text="Profil", pady=83, padx=110, bd=0, command=show_profile)
    profile_button_menu.grid(row=0, column=0 , sticky="ew")
    courses_button_menu = Button(menu_frame, text="Materii", pady=83, padx=110, bd=0, command=show_current_courses)
    courses_button_menu.grid(row=0, column=1, sticky="ew", padx=10)
    timetable_button_menu = Button(menu_frame, text="Orar", pady=83, padx=110, bd=0, command=show_timetable)
    timetable_button_menu.grid(row=0, column=2, sticky="ew")
    hobbies_button_menu = Button(menu_frame, text="Hobbies", pady=83, padx=110, bd=0, command=show_users_hobbies)
    hobbies_button_menu.grid(row=1, column=0, sticky="ew", pady=10)
    schedule_button_menu = Button(menu_frame, text="Program", pady=83, padx=110, bd=0)
    schedule_button_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
    session_schedule_button_menu = Button(menu_frame, text="Sesiune", pady=81, padx=90, bd=0)
    session_schedule_button_menu.grid(row=1, column=2, sticky="ew", pady=10)
    carnet_button_menu = Button(menu_frame, text="Carnet", pady=83, padx=110, bd=0, command=show_report_card)
    carnet_button_menu.grid(row=2, column=0 , sticky="ew")
    exams_button_menu = Button(menu_frame, text="Examene", pady=83, padx=110, bd=0, command=show_exams)
    exams_button_menu.grid(row=2, column=1, sticky="ew", padx=10)
    notifications_button_menu = Button(menu_frame, text="Notificari", pady=83, padx=110, bd=0)
    notifications_button_menu.grid(row=2, column=2, sticky="ew")


# Functia permite utilizatorilor noi se inregistreze
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
    profile_register_label = Label(frame_register, text="Domeniul: ")
    profile_register_label.grid(row=6, column=0, sticky=W, pady=(4,0))
    specialization_register_label = Label(frame_register, text="Specializare: ")
    specialization_register_label.grid(row=7, column=0, sticky=W, pady=(4,0))
    year_register_label = Label(frame_register, text="Anul de studiu: ")
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
    first_name_register_input = Entry(frame_register, width=30)
    first_name_register_input.grid(row=0, column=1, padx=15)
    last_name_register_input = Entry(frame_register, width=30)
    last_name_register_input.grid(row=1, column=1)
    username_register_input = Entry(frame_register, width=30)
    username_register_input.grid(row=2, column=1)
    password_register_input = Entry(frame_register, width=30, show="*")
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
    year_register_drop = ttk.Combobox(frame_register, value=study_years)
    year_register_drop.grid(row=8, column=1, pady=(4,0))
    year_register_drop.current(0)

    submit_button_register = Button(frame_register, text="Inregistrare", command=register_database_function)
    submit_button_register.grid(row=10, column=0, columnspan=2, pady=10, ipadx=125)


# Functia afiseaza pe ecran aplicatia
def application_on():
    root.bind('<Return>', login_function)
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


application_on()


root.mainloop()

