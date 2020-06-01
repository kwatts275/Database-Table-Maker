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
from tkcalendar import Calendar, DateEntry
import TkTreectrl as treectrl
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
	export_file =  filedialog.askopenfilename(title = "Select file",filetypes = (("all files","*.*"),("csv files","*.csv")))
	e3.delete(0,'end')
	e3.insert(0,export_file)

def save_defaults(table_name,export_file):
	default_values = open(default_file,"w+")
	default_values.write(table_name+"\n")
	default_values.write(export_file+"\n")
	default_values.close()

def main_program():
	table_name = e2.get()
	export_file = e3.get()
	save_defaults(table_name,export_file)

	mydb = mysql.connector.connect(
		host=hostname,
		user=username,
		passwd=passwd,
		database=database_name
		)
	mycursor = mydb.cursor()

	sql_cmd = "SELECT field_name,field_label,data_type,field_len,link_table,sort_order,parent_table FROM table_details where table_name = '"+table_name+"' ORDER BY sort_order"
	print(sql_cmd)
	mycursor.execute(sql_cmd)

	# get the field names
	sql_cmd2 = "SELECT identifier,modified_by,modified_on,removed"
	headers = ["Identifier", "Modified By", "Modified On", "Removed"]
	field_labels = []
	field_names = []
	for x in mycursor:
		field_names.append(x[0])
		field_labels.append(x[1])
		sql_cmd2 += ","+x[0]
		headers.append(x[1])
	sql_cmd2 += " FROM "+table_name+" ORDER BY identifier"
	print(sql_cmd2)
	mycursor.execute(sql_cmd2)

	with open(export_file,"w+") as csvfile:
		f1 = csv.writer(csvfile,delimiter=",")
		f1.writerow(headers)
		for row in mycursor:
			f1.writerow(row)

def get_tables():
	print("database "+database_name)
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
	mycursor = mydb.cursor()
	mycursor.execute("SHOW TABLES")
	table_list = []
	for x in mycursor:
		table_list.append(x[0])
	e2['values']=table_list

def do_edit():
	fname = e3.get()
	if (shutil.which("cygstart") != None):
	    edit_cmd = "cygstart \"" + fname + "\""
	elif (shutil.which("libreoffice") != None):
	    edit_cmd = "libreoffice \"" + fname + "\""
	else:
	    edit_cmd = "gedit \"" + fname + "\""
	os.system(edit_cmd)

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

w3 = Label(frame3, text="Export File: ",font=("Times",16)).pack(side="left")
export_file = default_values.readline()
e3 = Entry(frame3,width=40,font=("Times",16))
e3.insert(0, export_file.strip())
e3.pack(in_=frame3,side="left")
btn1 = Button(frame3,text='Search',font=("Times",16),command=get_file).pack(side="left")

btn3 = Button(framebot,text='Go',font=("Times",16),command=main_program).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")
btn5 = Button(framebot,text='View Results',font=("Times",16),command=do_edit).pack()

default_values.close()

table_list = []
get_tables()

mw.mainloop()
