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
from table_maker_config import hostname,username,ciphered_passwd,database_name
from cryptography.fernet import Fernet
import csv
import shutil
from pathlib import Path

__author__ = "Kenneth A. Watanabe"
__copyright__ = "Copyright (C) 2020 Kenneth Watanabe"
__license__ = "Public Domain"
__version__ = "4.0"

def get_file():
	import_file =  filedialog.askopenfilename(title = "Select file",filetypes = (("all files","*.*"),("csv files","*.csv")))
	e3.delete(0,'end')
	e3.insert(0,import_file)

def save_defaults(table_name,import_file):
	default_values = open(default_file,"w+")
	default_values.write(table_name+"\n")
	default_values.write(import_file+"\n")
	default_values.close()

def main_program():
    table_name = e2.get()
    import_file = e3.get()
    save_defaults(table_name,import_file)

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')

    f1 = open(import_file,"rb")
    line_number = 0
    sqlcmd = ""
    with open(import_file) as csv_file:
        csv_reader = csv.reader(csv_file,delimiter=",")
        line_number = 0
        for row in csv_reader:
            if line_number == 0:
                field_names = row
            else:
                sqlcmd = "INSERT INTO "+e2.get()+" (modified_by,modified_on"
                for field_name in field_names:
                    sqlcmd += ","+field_name.strip()
                sqlcmd += ") VALUES ('"+getpass.getuser()+"','"+cur_time+"'"
                for field_value in row:
                    field_value = field_value.replace("'","\`") # Replace single quotes with a back tic since single quotes cause problems
                    sqlcmd += ",'"+field_value.strip()+"'"
                sqlcmd = sqlcmd.rstrip(",") # remove trailing comma
                sqlcmd += ")"
            print(sqlcmd)
            mycursor.execute(sqlcmd)
            line_number+=1
    mydb.commit()
    f1.close()
    msg_text = "Records imported into "+e2.get()
    messagebox.showinfo("Information",msg_text)

def get_template():
	if e2.get() == "":
		return
	mydb = mysql.connector.connect(
		host=hostname,
		user=username,
		passwd=passwd,
		database=database_name
		)
	mycursor = mydb.cursor()
	now = datetime.now()
	cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
	sql_cmd = "SELECT field_name FROM table_details WHERE (table_name = '"+e2.get()+"') and (removed = 0)"
	mycursor.execute(sql_cmd)
	out_line = ""
	for x in mycursor:
		out_line += x[0]+","
	out_line.rstrip(",")

	temp_file = "template_file.csv"
	tmp_file = open(temp_file,"w+")
	tmp_file.write(out_line+"\n")
	tmp_file.close()
	if (shutil.which("cygstart") != None):
		edit_cmd = "cygstart \"" + temp_file + "\""
	elif (shutil.which("libreoffice") != None):
	    edit_cmd = "libreoffice \"" + temp_file + "\""
	else:
	    edit_cmd = "gedit \"" + temp_file + "\""
	os.system(edit_cmd)

def get_tables():
	print("database "+database_name)
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
	mycursor = mydb.cursor()
	sql_cmd = "SELECT table_name FROM table_header ORDER BY table_name"
	mycursor.execute(sql_cmd)
	table_list = []
	for x in mycursor:
            table_list.append(x[0])
	e2['values']=table_list


current_file = Path(__file__).stem
mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('700x200+400+200')
mw.title(current_file)

default_file = expanduser("~")+"/table_maker/"+current_file+".default"
# If file does not exist, create one
if not os.path.isfile(default_file):
		cmd = "touch " + default_file
		os.system(cmd)
default_values = open(default_file,"r")


frame1 = Frame(mw)
frame2 = Frame(mw)
frame3 = Frame(mw)
framebot = Frame(mw)
frame1.pack(side=TOP,fill=X)
frame2.pack(side=TOP,fill=X)
frame3.pack(side=TOP,fill=X)
framebot.pack(side=BOTTOM,fill=X)

KEY_FILE = "/home/table_maker/key.key"
key = ""
unciphered_passwd = ""
if os.path.isfile(KEY_FILE):
	file = open(KEY_FILE, 'rb')
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

w2 = Label(frame2, text="Table Name: ",font=("Times",16)).pack(side="left")
table_name = default_values.readline()
e2 = ttk.Combobox(frame2,width=40,font=("Times",16))
e2.insert(0,table_name.strip())
e2.pack(in_=frame2,side="left")

w3 = Label(frame3, text="Import File: ",font=("Times",16)).pack(side="left")
import_file = default_values.readline()
e3 = Entry(frame3,width=40,font=("Times",16))
e3.insert(0, import_file.strip())
e3.pack(in_=frame3,side="left")
btn1 = Button(frame3,text='Search',font=("Times",16),command=get_file).pack(side="left")

btn3 = Button(framebot,text='Go',font=("Times",16),command=main_program).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")
btn3 = Button(framebot,text='Template',font=("Times",16),command=get_template).pack()
#btn5 = Button(framebot,text='View Results',font=("Times",16),command=do_edit).pack()

default_values.close()

table_list = []
get_tables()

mw.mainloop()
