from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as font
import os.path
from os.path import expanduser
import os
import mysql.connector
import getpass
from datetime import datetime
from table_maker_config import hostname,username,ciphered_passwd
from cryptography.fernet import Fernet

class Lotfi(Entry):
    def __init__(self, master=None, **kwargs):
        self.var = StringVar()
        Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self.get().isdigit():
            # the current value is only digits; allow this
            self.old_value = self.get()
        elif self.get() == "":
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)


def data_table(frame4):

    datatypes=["VARCHAR","INT","DATE","FLOAT","BOOLEAN"]

    # Create a 6x7 array of zeros as the one you used
    for i in range(0,max_rows):
               j = 0
               values.append([])
               values[i].append(Entry(frame4))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Entry(frame4))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Combobox(frame4,values=datatypes))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Lotfi(frame4))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Entry(frame4))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Lotfi(frame4))
               values[i][j].grid(row=i,  column= j)


def save_defaults(dbase,table_name):
	default_values = open(default_file,"w+")
	default_values.write(dbase+"\n")
	default_values.write(table_name+"\n")
	default_values.close()

def main_program():
    dbase = a1.get()
    table_name = a2.get()
    save_defaults(dbase,table_name)

    key_file = expanduser("~")+"/python/key.key"
    key = ""
    unciphered_passwd = ""
    if os.path.isfile(key_file):
        file = open(key_file, 'rb')
        key = file.read() # The key will be type bytes
        file.close()
        cipher_suite = Fernet(key)
        byte_ciphered_passwd = str.encode(ciphered_passwd)
        byte_unciphered_passwd = (cipher_suite.decrypt(byte_ciphered_passwd))
        passwd = byte_unciphered_passwd.decode("utf-8")
    else:
        msg_text = "Cannot find password key "
        messagebox.showerror("Error",msg_text)
        return

    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd
        )
    mycursor = mydb.cursor()

    sql_cmd = "CREATE DATABASE IF NOT EXISTS "+dbase
    mycursor.execute(sql_cmd)

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=dbase
            )
    mycursor = mydb.cursor()

    mycursor.execute("SHOW TABLES")
    table_exists = 0
    for x in mycursor:
        if x[0] == table_name:
            table_exists = 1

    if table_exists == 1:
        msg_text = "Table "+table_name+" already exists."
        messagebox.showerror("Error",msg_text)
        return

    # Create table_details table to store the table field names and their labels
    sql_cmd = "CREATE TABLE IF NOT EXISTS table_details"
    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
    sql_cmd += "modified_by varchar(50),"
    sql_cmd += "modified_on date,"
    sql_cmd += "table_name varchar(50),"
    sql_cmd += "field_name varchar(50),"
    sql_cmd += "field_label varchar(50),"
    sql_cmd += "data_type varchar(10),"
    sql_cmd += "field_len integer,"
    sql_cmd += "link_table varchar(50),"
    sql_cmd += "sort_order integer,"
    sql_cmd += "parent_table varchar(50))"
    mycursor.execute(sql_cmd)
    print(sql_cmd+"\n")


    sql_cmd = "CREATE TABLE IF NOT EXISTS "+table_name
    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
    sql_cmd += "modified_by varchar(50),"
    sql_cmd += "modified_on datetime,"
    sql_cmd += "removed boolean default 0"

    sql_cmd2 = "CREATE TABLE IF NOT EXISTS "+table_name+"_aud"
    sql_cmd2 += " (identifier integer,"
    sql_cmd2 += "modified_by varchar(50),"
    sql_cmd2 += "modified_on datetime,"
    sql_cmd2 += "removed boolean default 0"

    i = 0;
    field_name = values[i][0].get()
    field_label = values[i][1].get()
    data_type = values[i][2].get()
    data_type = data_type.upper()
    field_len = values[i][3].get()
    link_table = values[i][4].get()
    sort_order = values[i][5].get()
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    while (field_name != "") and (i < max_rows):
            if (data_type == "VARCHAR") or (data_type == "varchar"):
                sql_cmd += ","+field_name+" "+data_type+"("+field_len+")"
                sql_cmd2 += ","+field_name+" "+data_type+"("+field_len+")"
            else:
                sql_cmd += ","+field_name+" "+data_type
                sql_cmd2 += ","+field_name+" "+data_type

            if (field_len == ""):
                field_len = "NULL"
            if (sort_order == ""):
                sort_order = "NULL"
            sql_cmd3 = "insert into table_details (table_name,modified_by,modified_on,field_name,field_label,data_type,field_len,link_table,sort_order) values ('"
            sql_cmd3 += table_name+"','"+getpass.getuser()+"','"+cur_time+"','"+field_name+"','"+field_label+"','"+data_type+"',"+field_len+",'"+link_table+"',"+sort_order+")"
            print(sql_cmd3)
            mycursor.execute(sql_cmd3)

            values[i][0].configure(state="readonly")
            values[i][1].configure(state="readonly")
            values[i][2].configure(state="readonly")
            values[i][3].configure(state="readonly")
            values[i][4].configure(state="readonly")
            values[i][5].configure(state="readonly")

            i += 1
            field_name = values[i][0].get()
            field_label = values[i][1].get()
            data_type = values[i][2].get()
            data_type = data_type.upper()
            field_len = values[i][3].get()
            link_table = values[i][4].get()
            sort_order = values[i][5].get()

    sql_cmd += ")"
    sql_cmd2 += ")"
    mycursor.execute(sql_cmd)
    mycursor.execute(sql_cmd2)
    mydb.commit()
    print(sql_cmd+"\n")
    msg_text = "Table Created "+a2.get()
    messagebox.showinfo("Information",msg_text)
    print("Finished\n")

def get_tables(event):
    print("database "+a1.get())
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=a1.get()
            )
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")
    table_list = []
    for x in mycursor:
        if (x[0].find("_aud") < 0):
            table_list.append(x[0])
    a2['values']=table_list

def init_tables(dbase):
    if (dbase != ""):
        print("database "+dbase)
        mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=a1.get()
            )
        mycursor = mydb.cursor()
        mycursor.execute("SHOW TABLES")
        table_list = []
        for x in mycursor:
            if (x[0].find("_aud") < 0):
                table_list.append(x[0])
        a2['values']=table_list

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=900,height=350)


# Start the main program here
if __name__ == "__main__":
    current_file = __file__
    mw=Tk()
    mw.geometry('900x500+200+150')
    mw.title(current_file)

    dot_pos = current_file.find(".")
    default_file = current_file[0:dot_pos]+".default"
    # If file does not exist, create one
    if not os.path.isfile(default_file):
    		cmd = "touch " + default_file
    		os.system(cmd)
    default_values = open(default_file,"r")

    frame1 = Frame(mw)
    frame2 = Frame(mw)
    frame3 = Frame(mw)
    frame4 = Frame(mw)
    framebot = Frame(mw)
    frame1.pack(side=TOP,fill=X)
    frame2.pack(side=TOP,fill=X)
    frame3.pack(side=TOP,fill=X)
    frame4.pack(side=TOP,fill=X)
    framebot.pack(side=BOTTOM,fill=X)

    key_file = expanduser("~")+"/python/key.key"
    key = ""
    unciphered_passwd = ""
    if os.path.isfile(key_file):
        file = open(key_file, 'rb')
        key = file.read() # The key will be type bytes
        file.close()
        cipher_suite = Fernet(key)
        byte_ciphered_passwd = str.encode(ciphered_passwd)
        byte_unciphered_passwd = (cipher_suite.decrypt(byte_ciphered_passwd))
        global passwd
        passwd = byte_unciphered_passwd.decode("utf-8")
    else:
        msg_text = "Cannot find password key"
        messagebox.showerror("Error",msg_text)
        exit()

    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd
        )
    mycursor = mydb.cursor()

    mycursor.execute("SHOW DATABASES")
    dbase_list = []
    table_list = []
    for x in mycursor:
        dbase_list.append(x[0])

    w1 = Label(frame1, text="Database Name: ",font=("Times",16)).pack(side="left")
    dbase = default_values.readline()
    a1 = ttk.Combobox(frame1,width=40,font=("Times",16),values=dbase_list)
    a1.bind("<<ComboboxSelected>>",get_tables)
    a1.insert(0,dbase.strip())
    a1.pack(side="left")

    w2 = Label(frame2, text="Table Name: ",font=("Times",16)).pack(side="left")
    table_name = default_values.readline()
    a2 = ttk.Combobox(frame2,width=40,font=("Times",16))
    a2.insert(0,table_name.strip())
    a2.pack(side="left")

    l1 = Entry(frame3,relief=FLAT)
    l1.insert(0,"Field Name")
    l1.config(state="readonly")
    l1.grid(row=0,column= 0)

    l2 = Entry(frame3,relief=FLAT)
    l2.insert(0,"Column Label")
    l2.config(state="readonly")
    l2.grid(row=0,column= 1)

    l3 = Entry(frame3,relief=FLAT)
    l3.insert(0,"Data Type")
    l3.config(state="readonly")
    l3.grid(row=0,column= 2)

    l4 = Entry(frame3,relief=FLAT)
    l4.insert(0,"Length")
    l4.config(state="readonly")
    l4.grid(row=0,column= 3)

    l5 = Entry(frame3,relief=FLAT)
    l5.insert(0,"Link Table")
    l5.config(state="readonly")
    l5.grid(row=0,column= 4)

    l6 = Entry(frame3,relief=FLAT)
    l6.insert(0,"Sort Order")
    l6.config(state="readonly")
    l6.grid(row=0,column= 5)

    init_tables(a1.get())

    btn3 = Button(framebot,text='Create Table',font=("Times",16),command=main_program).pack(side="left")
    btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")

    default_values.close()

    canvas=Canvas(frame4)
    frame=Frame(canvas)
    myscrollbar=Scrollbar(frame4,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",myfunction)

    values = []
    max_rows = 20
    data_table(frame)
    mw.mainloop()
