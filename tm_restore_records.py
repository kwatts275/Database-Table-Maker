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
from pathlib import Path

__author__ = "Kenneth A. Watanabe"
__copyright__ = "Copyright (C) 2020 Kenneth Watanabe"
__license__ = "Public Domain"
__version__ = "4.0"

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
        if self.get() == "":
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)


def save_defaults(table_name):
	default_values = open(default_file,"w+")
	default_values.write(table_name+"\n")
	default_values.close()

def get_record():
	if field_id_var.get() == "":
		return True
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
	mycursor = mydb.cursor()

	global orig_mb
	global orig_mo
	global orig_values
	orig_values = []

	sql_cmd = "select identifier,modified_by,modified_on"
	for x in field_names:
		sql_cmd += ","+x
	sql_cmd += " from "+e2.get()+" where identifier = "+field_id_var.get()
	print(sql_cmd)
	mycursor.execute(sql_cmd)
	for row in mycursor:
		field_mb_var.set(row[1])
		field_mo_var.set(row[2])
		orig_mb = row[1]
		orig_mo = row[2]
		i = 0
		for x in field_entries:
			x.delete(0,END)
			if row[i+3] != None:
				x.insert(0,row[i+3])
			orig_values.append(row[i+3])
			i += 1
	return True

def select_cmd(event):
	info = mlb.listbox.identify(event.x, event.y)
	if info[0] == 'item':
		field_id_var.set(identifiers[info[1]-1])
		print("Selected item:" + str(info[1]-1))
		find_window.destroy()

def sort_list(event):
	index = str(event.column)
	mlb.listbox.sort(column=event.column, mode=sortorder_flags[index])
	if sortorder_flags[index] == 'increasing':
		mlb.listbox.column_configure(mlb.listbox.column(event.column), arrow='up')
		sortorder_flags[index] = 'decreasing'
	else:
		mlb.listbox.column_configure(mlb.listbox.column(event.column), arrow='down')
		sortorder_flags[index] = 'increasing'


def select_record():
	global find_window
	find_window = Toplevel(mw)
	find_window.geometry('700x300+400+200')
	find_window.title('Select Record')
	global mlb
	mlb = treectrl.ScrolledMultiListbox(find_window)
	mlb.pack(side='top', fill='both', expand=1)
	mlb.focus_set()
	mlb.listbox.config(columns=['identifier'] + field_labels,selectmode='extended')
	sql_cmd = "SELECT identifier"
	for x in field_names:
		sql_cmd += ","+x
	sql_cmd += " from "+e2.get()+" where removed = '1'"
	print("SQL cmd: "+sql_cmd)
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
	mycursor = mydb.cursor()
	mycursor.execute(sql_cmd)
	global identifiers
	identifiers = []
	global last_names
	last_names = []
	for row in mycursor:
		identifiers.append(row[0])
		last_names.append(row[1])
		mlb.listbox.insert('end',*map(str,row))
	mlb.listbox.bind('<1>', select_cmd)
	mlb.listbox.notify_install('<Header-invoke>')
	mlb.listbox.notify_bind('<Header-invoke>', sort_list)

	global sortorder_flags
	sortorder_flags = {}
	for i in range(number_of_fields):
		sortorder_flags[str(i)] = "increasing"

def main_program():
	table_name = e2.get()
	save_defaults(table_name)

	new_window = Toplevel(mw)
	new_window.wm_title("Restore "+table_name+" Record")
	new_window.geometry('920x550+250+150')

	new_frame1 = Frame(new_window)
	new_frame2 = Frame(new_window)
	new_frame3 = Frame(new_window)
	new_frame1.pack(side=TOP,fill=X)
	new_frame2.pack(side=TOP,fill=X)
	new_frame3.pack(side=BOTTOM,fill=X)

	label1 = Label(new_frame1, text="Identifier",font=("Times",16))
	label1.grid(row=0,column=0)
	global field_id_var
	field_id_var = StringVar()
	field_id = Entry(new_frame1,width=40,font=("Times",16),textvariable = field_id_var,validate="focusout",validatecommand=get_record)
	field_id.grid(row=0,column=1)

	find_button = Button(new_frame1,text='Find',font=("Times",16),command=select_record)
	find_button.grid(row=0,column=2)


	label1 = Label(new_frame1, text="Modified By",font=("Times",16))
	label1.grid(row=1,column=0)
	global field_mb_var
	field_mb_var = StringVar()
	field_mb = Entry(new_frame1,width=40,font=("Times",16),state="readonly",textvariable=field_mb_var)
	field_mb.grid(row=1,column=1)

	label1 = Label(new_frame1, text="Modified On",font=("Times",16))
	label1.grid(row=2,column=0)
	global field_mo_var
	field_mo_var = StringVar()
	field_mo = Entry(new_frame1,width=40,font=("Times",16),state="readonly",textvariable=field_mo_var)
	field_mo.grid(row=2,column=1)

	# Get table fields
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
	mycursor = mydb.cursor()
	sql_cmd = "select field_name,field_label,data_type,field_len,link_table,sort_order,parent_table from table_details where table_name = '"+table_name+"'"
	#print(sql_cmd)
	mycursor.execute(sql_cmd)

	# Must make arrays global so that they can be accessed from update_record routine
	global field_labels
	field_labels = []
	global field_names
	field_names = []
	global field_entries
	field_entries = []

	i = 0
	for x in mycursor:
		# If table is a child table, add a prompt for the parent record
		if i == 0:
			if (x[6] != None) and (x[6] != ""):
				field_names.append(x[6])
				field_labels.append(x[6])
				label1 = Label(new_frame2, text=x[6],font=("Times",16))
				label1.grid(row=i,column=0)
				field_entries.append(Lotfi(new_frame2,width=11,font=("Times",16)))
				field_entries[i].grid(sticky="w",row=i,column=1)
				i += 1

		field_names.append(x[0])
		field_labels.append(x[1])
		# print(field_names[i]+" "+field_labels[i])

		label1 = Label(new_frame2, text=x[1],font=("Times",16))
		label1.grid(row=i,column=0)
		if (x[2] == "DATE"):
			field_entries.append(DateEntry(new_frame2,width=40,font=("Times",16),date_pattern="Y-mm-dd"))
		else:
			field_entries.append(Entry(new_frame2,width=x[3],font=("Times",16)))
		field_entries[i].grid(sticky="w",row=i,column=1)
		i+=1
	global number_of_fields
	number_of_fields = i
	save_button = Button(new_frame3,text='Restore Record',font=("Times",16),command=lambda:update_record(new_window)).pack(side="left")
	exit_button = Button(new_frame3,text='Exit',font=("Times",16),command=new_window.destroy).pack(side="right")


def update_record(new_window):
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
	mycursor = mydb.cursor()
	now = datetime.now()
	cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
	sql_cmd = "UPDATE "+e2.get()+" SET modified_by = '"+getpass.getuser()+"',modified_on = '"+str(cur_time)+"',"
	sql_cmd += "removed = '0' where identifier = "+field_id_var.get()
	print(sql_cmd)
	mycursor.execute(sql_cmd)

	sql_cmd2 = "INSERT INTO "+e2.get()+"_aud (identifier,modified_by,modified_on,removed"
	for x in field_names:
		sql_cmd2 += ","+x
	sql_cmd2 += ") VALUES ("+field_id_var.get()+",'"+orig_mb+"','"+str(orig_mo)+"','1'"
	for x in range(number_of_fields):
		if (orig_values[x] == None):
			temp_var = ""
		else:
			temp_var = str(orig_values[x])
		sql_cmd2 += ",'"+temp_var+"'"
	sql_cmd2 += ")"
	mycursor.execute(sql_cmd2)
	mydb.commit()

	field_id_var.set("")
	field_mb_var.set("")
	field_mo_var.set("")
	for x in field_entries:
		x.delete(0,END)
	msg_text = "Record Restored "+str(field_id_var.get())
	messagebox.showinfo("Information",msg_text,parent=new_window)

def get_tables(event):
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
		if (x[0].find("_aud") < 0):
			table_list.append(x[0])
	e2['values']=table_list

def init_tables(dbase):
        print("database "+dbase)
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
            if (x[0].find("_aud") < 0):
                table_list.append(x[0])
        e2['values']=table_list

current_file = Path(__file__).stem
mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('600x200+400+200')
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


w2 = Label(frame2, text="Table Name: ",font=("Times",16)).pack(side="left")
table_name = default_values.readline()
e2 = ttk.Combobox(frame2,width=40,font=("Times",16))
e2.insert(0,table_name.strip())
e2.pack(in_=frame2,side="left")


btn3 = Button(framebot,text='Go',font=("Times",16),command=main_program).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")

default_values.close()

init_tables(database_name)

mw.mainloop()
