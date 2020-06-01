from tkinter import *
from tkinter import ttk
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
		elif self.get() == "":
			self.old_value = self.get()
		else:
			# there's non-digit characters in the input; reject this
			self.set(self.old_value)

def save_defaults(*args):
	default_values = open(default_file,"w+")
	for x in args:
		default_values.write(x+"\n")
	default_values.close()

def main_program():
	field_name = e1.get()
	field_value = e2.get()
	inc_value = e3.get()
	save_defaults(field_name,field_value)
	mydb = mysql.connector.connect(
		host=hostname,
		user=username,
		passwd=passwd,
		database=database_name
		)
	mycursor = mydb.cursor()
	sql_cmd = "SELECT increment FROM increment WHERE (field_name = '"+field_name+"') AND (field_value = '"+field_value+"')"
	mycursor.execute(sql_cmd)
	row = mycursor.fetchone()
	if row == None:
		sql_cmd = "INSERT INTO increment (field_name, field_value, increment) VALUES ('"+field_name+"','"+field_value+"',"+inc_value+")"
	else:
		sql_cmd = "UPDATE increment SET increment = "+inc_value+" WHERE (field_name = '"+field_name+"') AND (field_value = '"+field_value+"')"
	print(sql_cmd)
	mycursor.execute(sql_cmd)
	mydb.commit()

	msg_text = "Increment Saved"
	messagebox.showinfo("Information",msg_text)
	print("Finished\n")

def get_current_increment():
	field_name = e1.get()
	field_value = e2.get()
	mydb = mysql.connector.connect(
		host=hostname,
		user=username,
		passwd=passwd,
		database=database_name
		)
	mycursor = mydb.cursor()
	sql_cmd = "SELECT increment FROM increment WHERE (field_name = '"+field_name+"') AND (field_value = '"+field_value+"')"
	print(sql_cmd)
	mycursor.execute(sql_cmd)
	row = mycursor.fetchone()
	if row == None:
		e3.delete(0,END)
		e3.insert(0,"0")
	else:
		e3.delete(0,END)
		e3.insert(0,row[0])

def test_increment(field_name,field_value):
	inc_value = increment(field_name,field_value)
	e3.delete(0,END)
	e3.insert(0,inc_value)

def increment(field_name,field_value):

	mydb = mysql.connector.connect(
		host=hostname,
		user=username,
		passwd=passwd,
		database=database_name
		)
	mycursor = mydb.cursor()
	sql_cmd = "SELECT increment FROM increment WHERE (field_name = '"+field_name+"') AND (field_value = '"+field_value+"')"
	print(sql_cmd)
	mycursor.execute(sql_cmd)
	row = mycursor.fetchone()
	if row == None:
		inc_value = 1
		sql_cmd = "INSERT INTO increment (field_name, field_value, increment) VALUES ('"+field_name+"','"+field_value+"',"+str(inc_value)+")"
	else:
		inc_value = row[0] + 1
		sql_cmd = "UPDATE increment SET increment = "+str(inc_value)+" WHERE (field_name = '"+field_name+"') AND (field_value = '"+field_value+"')"
	mycursor.execute(sql_cmd)
	mydb.commit()
	return(inc_value)

current_file = __file__
mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('700x200+400+200')
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

w1 = Label(frame1, text="Field Name: ",font=("Times",16)).pack(side="left")
field_name = default_values.readline()
e1 = Entry(frame1,width=40,font=("Times",16))
e1.insert(0,field_name.strip())
e1.pack(side="left")


w2 = Label(frame2, text="Field Value: ",font=("Times",16)).pack(side="left")
field_value = default_values.readline()
e2 = Entry(frame2,width=40,font=("Times",16))
e2.insert(0,field_value.strip())
e2.pack(side="left")

w3 = Label(frame3, text="Increment: ",font=("Times",16)).pack(side="left")
e3 = Lotfi(frame3,width=40,font=("Times",16))
e3.pack(side="left")

btn1 = Button(framebot,text='Save Changes',font=("Times",16),command=main_program).pack(side="left")
btn2 = Button(framebot,text='Get Current Increment',font=("Times",16),command=get_current_increment).pack(side="left")
btn3 = Button(framebot,text='Test Increment Function',font=("Times",16),command=lambda:test_increment(e1.get(),e2.get())).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")

default_values.close()

mw.mainloop()
