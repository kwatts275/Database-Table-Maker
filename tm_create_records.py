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
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)

def save_defaults(dbase,table_name):
	default_values = open(default_file,"w+")
	default_values.write(dbase+"\n")
	default_values.write(table_name+"\n")
	default_values.close()

def main_program():
	dbase = e1.get()
	table_name = e2.get()
	save_defaults(dbase,table_name)

	new_window = Toplevel(mw)
	new_window.wm_title("Create New "+dbase+" Record")
	new_window.geometry('700x400+400+200')

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
	field_id = Entry(new_frame1,width=40,font=("Times",16),state="readonly",textvariable = field_id_var)
	field_id.grid(row=0,column=1)

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
            database=dbase
            )
	mycursor = mydb.cursor()
	sql_cmd = "select field_name,field_label,data_type,field_len,link_table,sort_order,parent_table from table_details where table_name = '"+table_name+"' order by sort_order"
	#print(sql_cmd)
	mycursor.execute(sql_cmd)

	field_labels = []
	# Must make field_names and field_entries global so that they can be accessed from create_record routine
	global field_names
	field_names = []
	global field_entries
	field_entries = []

	i = 0
	for x in mycursor:
		field_names.append(x[0])
		field_labels.append(x[1])
		# print(field_names[i]+" "+field_labels[i])

		label1 = Label(new_frame2, text=x[1],font=("Times",16))
		label1.grid(row=i,column=0)
		if (x[4] != ""): # Link table
			record_list=[]
			get_dropdown(x[4],record_list)
			field_entries.append(ttk.Combobox(new_frame2,width=x[3]+1,font=("Times",16),values=record_list))
		elif (x[2] == "DATE"):
			field_entries.append(DateEntry(new_frame2,width=40,font=("Times",16),date_pattern="Y-mm-dd"))
		elif (x[2] == "INT"):
			field_entries.append(Lotfi(new_frame2,width=11,font=("Times",16)))
		else:
			field_entries.append(Entry(new_frame2,width=x[3],font=("Times",16)))
		field_entries[i].grid(sticky="w",row=i,column=1)
		i+=1
	save_button = Button(new_frame3,text='Create Record',font=("Times",16),command=create_record).pack(side="left")
#	exit_button = Button(new_frame3,text='Exit',font=("Times",16),command=new_window.destroy).pack(side="right")
	exit_button = Button(new_frame3,text='Exit',font=("Times",16),command=lambda:[mw.deiconify(),new_window.destroy()]).pack(side="right")
	mw.withdraw()	# hide main window


def create_record():
	mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=e1.get()
            )
	mycursor = mydb.cursor()
	sql_cmd = "INSERT INTO "+e2.get()+" (modified_by,modified_on"
	for x in field_names:
		sql_cmd += ","+x
	now = datetime.now()
	cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
	sql_cmd += ") VALUES ('"+getpass.getuser()+"','"+cur_time+"'"
	for x in field_entries:
		val = x.get()
		if val == '':
			sql_cmd += ",Null"
		else:
			sql_cmd += ",'"+x.get()+"'"
	sql_cmd += ")"

	print(sql_cmd)
	mycursor.execute(sql_cmd)
	mydb.commit()
	field_id_var.set(str(mycursor.lastrowid))
	field_mb_var.set(getpass.getuser())
	field_mo_var.set(cur_time)
	msg_text = "Record Created "+str(field_id_var.get())
	messagebox.showinfo("Information",msg_text)

	for x in field_entries:
		x.delete(0,END)


def do_edit():
	fname2 = e2.get()
	edit_cmd = "cygstart \"" + fname2 + "\"";
	os.system(edit_cmd)

def get_tables(event):
    print("database "+e1.get())
    e2.delete(0,END)
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=e1.get()
            )
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")
    table_list = []
    for x in mycursor:
        if (x[0].find("_aud") < 0):
            table_list.append(x[0])
    e2['values']=table_list

def init_tables(dbase):
    if (dbase != ""):
        print("database "+dbase)
        mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=dbase
            )
        mycursor = mydb.cursor()
        mycursor.execute("SHOW TABLES")
        table_list = []
        for x in mycursor:
            if (x[0].find("_aud") < 0):
                table_list.append(x[0])
        e2['values']=table_list

def get_dropdown(source,record_list):
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=e1.get()
        )
    mycursor = mydb.cursor()

    dot_pos = source.find(".")
    table_name = source[0:dot_pos]
    field_name = source[dot_pos+1:len(source)]
    sql_cmd = "select "+field_name+" from "+table_name
    mycursor.execute(sql_cmd)
    for x in mycursor:
	       record_list.append(x[0])

current_file = __file__
mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('600x200+400+200')
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
framebot = Frame(mw)
frame1.pack(side=TOP,fill=X)
frame2.pack(side=TOP,fill=X)
frame3.pack(side=TOP,fill=X)
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
e1 = ttk.Combobox(frame1,width=40,font=("Times",16),values=dbase_list)
e1.bind("<<ComboboxSelected>>",get_tables)
e1.insert(0,dbase.strip())
e1.pack(side="left")

w2 = Label(frame2, text="Table Name: ",font=("Times",16)).pack(side="left")
table_name = default_values.readline()
e2 = ttk.Combobox(frame2,width=40,font=("Times",16))
e2.insert(0,table_name.strip())
e2.pack(in_=frame2,side="left")

init_tables(e1.get())

btn3 = Button(framebot,text='Go',font=("Times",16),command=main_program).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")
#btn5 = Button(framebot,text='View Results',font=("Times",16),command=do_edit).pack()

default_values.close()

mw.mainloop()
