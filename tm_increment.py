from tkinter import *
from tkinter import ttk
import mysql.connector
import os.path
from os.path import expanduser
import os
from table_maker_config import hostname,username,ciphered_passwd,database_name
from cryptography.fernet import Fernet

__author__ = "Kenneth A. Watanabe"
__copyright__ = "Copyright (C) 2020 Kenneth Watanabe"
__license__ = "Public Domain"
__version__ = "4.0"

def increment(field_name,field_value):
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
	return(str(inc_value))


def get_record(table_name,values,record_id,parent_record):
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
		passwd=passwd,
		database=database_name
		)
	mycursor = mydb.cursor()
	if (str(parent_record) != "0"):
		sql_cmd = "SELECT parent_table FROM table_header WHERE table_name = '"+table_name+"'"
		print(sql_cmd)
		mycursor.execute(sql_cmd)
		row = mycursor.fetchone()
		parent_table = row[0]

	sql_cmd = "SELECT field_name,data_type FROM table_details WHERE table_name = '"+table_name+"'"
	print(sql_cmd)
	mycursor.execute(sql_cmd)
	sql_cmd = "SELECT identifier"
	field_names = ["identifier"]
	for row in mycursor:
		if (row[1] == "FLOAT"):
			sql_cmd += ",round("+row[0]+",2)"
		else:
			sql_cmd += ","+row[0]
		field_names.append(row[0])
	sql_cmd += " FROM "+table_name+" WHERE (removed = 0) "
	if (str(parent_record) != "0"):
		sql_cmd += "AND ("+parent_table+"="+parent_record+") "
	try:
		int(record_id)
		sql_cmd += "AND (identifier = "+str(record_id)+")"
	except ValueError:
		if (record_id.upper() == "LAST"):
			sql_cmd += "ORDER BY identifier DESC"
		elif (record_id.upper() == "FIRST"):
			sql_cmd += "ORDER BY identifier ASC"
		else:
			return(False)
	print(sql_cmd)
	mycursor.execute(sql_cmd)
	row = mycursor.fetchone()
	i = 0
	values.clear()
	if row == None:
		return(False)
	for x in row:
		values[field_names[i]] = x
		i += 1
	return(True)
