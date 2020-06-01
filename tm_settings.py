from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from cryptography.fernet import Fernet
import tkinter.font as font
import os.path
from os.path import expanduser
from pathlib import Path
import os
import mysql.connector
import getpass
from datetime import datetime

__author__ = "Kenneth A. Watanabe"
__copyright__ = "Copyright (C) 2020 Kenneth Watanabe"
__license__ = "Public Domain"
__version__ = "4.0"

def save_defaults(host,user,passwd,db):
	default_values = open(default_file,"w+")
	default_values.write(host+"\n")
	default_values.write(user+"\n")
	default_values.write(passwd.decode("utf-8")+"\n")
	default_values.write(db+"\n")
	default_values.close()

def main_program():
	host = e1.get()
	user = e2.get()
	passwd = e3.get()
	db = e4.get()

	key = Fernet.generate_key()
	file = open(key_file, 'wb')
	file.write(key) # The key is type bytes still
	file.close()
	cipher_suite = Fernet(key)
	ciphered_passwd = cipher_suite.encrypt(str.encode(passwd))
	save_defaults(host,user,ciphered_passwd,db)

	byte_passwd = (cipher_suite.decrypt(ciphered_passwd))
	unciphered_passwd = bytes(byte_passwd).decode("utf-8")

	# Put code here
	fname = "/home/table_maker/table_maker_config.py"
	f1 = open(fname,"w+")

	f1.write("hostname=\""+host+"\"\n")
	f1.write("username=\""+user+"\"\n")
	f1.write("ciphered_passwd=\""+str(ciphered_passwd.decode("utf-8"))+"\"\n")
	f1.write("database_name=\""+db+"\"\n")
	f1.close()
	msg_text = "Data Saved"
	messagebox.showinfo("Information",msg_text)
	print("Finished\n")

def test_connection():
	try:
		mydb = mysql.connector.connect(
	        host=e1.get(),
	        user=e2.get(),
	        passwd=e3.get()
	        )
		if mydb.is_connected():
		    dbinfo = mydb.get_server_info()
		    msg_text = "Connected to SQL database "+dbinfo
		    messagebox.showinfo("Information",msg_text)
	except mysql.connector.Error as e:
		msg_text = "Cannot connect to SQL database "+str(e)+"\nMake sure hostname,username and password are correct."
		messagebox.showerror("Error",msg_text)

	mycursor = mydb.cursor()
	mycursor.execute("SHOW DATABASES")
	dbase_list = []
	for x in mycursor:
		dbase_list.append(x[0])
	e4.configure(values=dbase_list)
	if (e4.get() != "") and (e4.get() not in dbase_list):
		dbase = e4.get()
		dash_pos = dbase.find("-")
		if (dash_pos >= 0):
		    msg_txt = "Error: You cannot have dashes (-) in a database name."
		    messagebox.showerror(title="Error",message=msg_txt)
		    return
		title = "Database does not exist"
		msg_txt = "Database "+dbase+" does not exist.\nDo you wish to create a new database?"
		response=messagebox.askyesno(title=title,message=msg_txt)
		if (response == True):
		    sql_cmd = "CREATE DATABASE "+e4.get()
		    mycursor.execute(sql_cmd)

		    mydb = mysql.connector.connect(
		            host=e1.get(),
		            user=e2.get(),
		            passwd=e3.get(),
		            database=e4.get()
		            )
		    mycursor = mydb.cursor()

		    # Create table_details table to store the table field names and their labels
		    sql_cmd = "CREATE TABLE IF NOT EXISTS increment"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "field_name varchar(50),"
		    sql_cmd += "field_value varchar(50),"
		    sql_cmd += "increment int)"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS table_header"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "table_name varchar(50),"
		    sql_cmd += "table_description varchar(255),"
		    sql_cmd += "parent_table varchar(50))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

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
		    sql_cmd += "parent_table varchar(50),"
		    sql_cmd += "removed boolean default 0)"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS query_header"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "query_name varchar(50),"
		    sql_cmd += "query_description varchar(255),"
		    sql_cmd += "table_name varchar(50),"
		    sql_cmd += "template_id int,"
		    sql_cmd += "sql_command varchar(1000))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS query_header_aud"
		    sql_cmd += " (identifier integer,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "query_name varchar(50),"
		    sql_cmd += "query_description varchar(255),"
		    sql_cmd += "table_name varchar(50),"
		    sql_cmd += "template_id int,"
		    sql_cmd += "sql_command varchar(1000))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    # Create table_details table to store the table field names and their labels
		    sql_cmd = "CREATE TABLE IF NOT EXISTS query_details"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on date,"
		    sql_cmd += "query_header integer,"
		    sql_cmd += "left_paren varchar(10),"
		    sql_cmd += "field_name varchar(50),"
		    sql_cmd += "operator varchar(10),"
		    sql_cmd += "field_value varchar(255),"
		    sql_cmd += "right_paren varchar(10),"
		    sql_cmd += "and_or varchar(6))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    # Create table_details table to store the table field names and their labels
		    sql_cmd = "CREATE TABLE IF NOT EXISTS query_columns"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on date,"
		    sql_cmd += "query_header integer,"
		    sql_cmd += "field_name varchar(50),"
		    sql_cmd += "field_label varchar(50),"
		    sql_cmd += "sort_order integer)"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    now = datetime.now()
		    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
		    sql_cmd = "INSERT INTO table_details (modified_by,modified_on,removed,table_name,field_name,field_label,data_type,field_len,sort_order) VALUES ('"
		    sql_cmd += getpass.getuser()+"','"+cur_time+"','0','query_header','query_name','Query Name','VARCHAR',50,1)"
		    mycursor.execute(sql_cmd)

		    sql_cmd = "INSERT INTO table_details (modified_by,modified_on,removed,table_name,field_name,field_label,data_type,field_len,sort_order) VALUES ('"
		    sql_cmd += getpass.getuser()+"','"+cur_time+"','0','query_header','query_description','Query Description','VARCHAR',255,2)"
		    mycursor.execute(sql_cmd)

		    sql_cmd = "INSERT INTO table_details (modified_by,modified_on,removed,table_name,field_name,field_label,data_type,field_len,sort_order) VALUES ('"
		    sql_cmd += getpass.getuser()+"','"+cur_time+"','0','query_header','table_name','Table Name','VARCHAR',50,3)"
		    mycursor.execute(sql_cmd)
		    mydb.commit()

		    sql_cmd = "CREATE TABLE IF NOT EXISTS dashboard_header"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "template_id int,"
		    sql_cmd += "dashboard_name varchar(50),"
		    sql_cmd += "dashboard_desc varchar(255))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS dashboard_header_aud"
		    sql_cmd += " (identifier integer,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "dashboard_name varchar(50),"
		    sql_cmd += "dashboard_desc varchar(255))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS dashboard_details"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "dashboard_header int,"
		    sql_cmd += "query_name varchar(50),"
		    sql_cmd += "sort_order int,"
		    sql_cmd += "ent boolean,"
		    sql_cmd += "category varchar(50),"
		    sql_cmd += "chart_type varchar(10),"
		    sql_cmd += "chart_title varchar(20))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS template_header"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "name varchar(50),"
		    sql_cmd += "descr varchar(255),"
		    sql_cmd += "num int,"
		    sql_cmd += "table_name varchar(50))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS template_header_aud"
		    sql_cmd += " (identifier integer,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "name varchar(50),"
		    sql_cmd += "descr varchar(255),"
		    sql_cmd += "num int,"
		    sql_cmd += "table_name varchar(50))"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    sql_cmd = "CREATE TABLE IF NOT EXISTS template_details"
		    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
		    sql_cmd += "modified_by varchar(50),"
		    sql_cmd += "modified_on datetime,"
		    sql_cmd += "removed boolean default 0,"
		    sql_cmd += "template_header int,"
		    sql_cmd += "disp boolean,"
		    sql_cmd += "ent boolean,"
		    sql_cmd += "copy boolean,"
		    sql_cmd += "mand boolean,"
		    sql_cmd += "field_name varchar(50),"
		    sql_cmd += "field_label varchar(50),"
		    sql_cmd += "def_value varchar(50),"
		    sql_cmd += "sort_order integer)"
		    print(sql_cmd)
		    mycursor.execute(sql_cmd)

		    now = datetime.now()
		    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
		    sql_cmd = "INSERT INTO table_details (modified_by,modified_on,removed,table_name,field_name,field_label,data_type,field_len,sort_order) VALUES ('"
		    sql_cmd += getpass.getuser()+"','"+cur_time+"','0','template_header','name','Template Name','VARCHAR',50,1)"
		    mycursor.execute(sql_cmd)

		    sql_cmd = "INSERT INTO table_details (modified_by,modified_on,removed,table_name,field_name,field_label,data_type,field_len,sort_order) VALUES ('"
		    sql_cmd += getpass.getuser()+"','"+cur_time+"','0','template_header','descr','Description','VARCHAR',255,2)"
		    mycursor.execute(sql_cmd)

		    sql_cmd = "INSERT INTO table_details (modified_by,modified_on,removed,table_name,field_name,field_label,data_type,field_len,sort_order) VALUES ('"
		    sql_cmd += getpass.getuser()+"','"+cur_time+"','0','template_header','table_name','Table Name','VARCHAR',50,3)"
		    mycursor.execute(sql_cmd)
		    mydb.commit()

		    msg_txt = "Database "+dbase+" created."
		    messagebox.showinfo(title="Info",message=msg_txt)


def get_file1():
	file1 =  filedialog.askopenfilename(title = "Select file",filetypes = (("all files","*.*"),("jpeg files","*.jpg"),("python files","*.py")))
	e1.delete(0,'end')
	e1.insert(0,file1)

def get_file2():
	file2 =  filedialog.askopenfilename(title = "Select file",filetypes = (("all files","*.*"),("jpeg files","*.jpg"),("python files","*.py")))
	e2.delete(0,'end')
	e2.insert(0,file2)

def check_reserved_words(str_value):
    if str_value.upper() in reserved_words:
            msg_text = "Invalid database name: "+str_value
            messagebox.showerror("Error",msg_text)
            return(False)
    return(True)

current_file = __file__
mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('700x250+400+200')
mw.title(current_file)

# MySQL reserved words. These words cannot be used for table or field names
reserved_words = ["ANALYZE","AND","AS","ASC","AUTO_INCREMENT","BDB","BERKELEYDB","BETWEEN","BIGINT","BINARY","BLOB","BOTH","BTREE","BY","CASCADE","CASE","CHANGE","CHAR","CHARACTER","CHECK","COLLATE","COLUMN","COLUMNS","CONSTRAINT","CREATE","CROSS","CURRENT_DATE","CURRENT_TIME","CURRENT_TIMESTAMP","DATABASE","DATABASES","DAY_HOUR","DAY_MINUTE","DAY_SECOND","DEC","DECIMAL","DEFAULT","DELAYED","DELETE","DESC","DESCRIBE","DISTINCT","DISTINCTROW","DIV","DOUBLE","DROP","ELSE","ENCLOSED","ERRORS","ESCAPED","EXISTS","EXPLAIN","FIELDS","FLOAT","FOR","FORCE","FOREIGN","FROM","FULLTEXT","FUNCTION","GEOMETRY","GRANT","GROUP","HASH","HAVING","HELP","HIGH_PRIORITY","HOUR_MINUTE","HOUR_SECOND","IF","IGNORE","IN","INDEX","INFILE","INNER","INNODB","INSERT","INT","INTEGER","INTERVAL","INTO","IS","JOIN","KEY","KEYS","KILL","LEADING","LEFT","LIKE","LIMIT","LINES","LOAD","LOCALTIME","LOCALTIMESTAMP","LOCK","LONG","LONGBLOB","LONGTEXT","LOW_PRIORITY","MASTER_SERVER_ID","MATCH","MEDIUMBLOB","MEDIUMINT","MEDIUMTEXT","MIDDLEINT","MINUTE_SECOND","MOD","MRG_MYISAM","NATURAL","NOT","NULL","NUMERIC","ON","OPTIMIZE","OPTION","OPTIONALLY","OR","ORDER","OUTER","OUTFILE","PRECISION","PRIMARY","PRIVILEGES","PROCEDURE","PURGE","READ","REAL","REFERENCES","REGEXP","RENAME","REPLACE","REQUIRE","RESTRICT","RETURNS","REVOKE","RIGHT","RLIKE","RTREE","SELECT","SET","SHOW","SMALLINT","SOME","SONAME","SPATIAL","SQL_BIG_RESULT","SQL_CALC_FOUND_ROWS","SQL_SMALL_RESULT","SSL","STARTING","STRAIGHT_JOIN","STRIPED","TABLE","TABLES","TERMINATED","THEN","TINYBLOB","TINYINT","TINYTEXT","TO","TRAILING","TYPES","UNION","UNIQUE","UNLOCK","UNSIGNED","UPDATE","USAGE","USE","USER_RESOURCES","USING","VALUES","VARBINARY","VARCHAR","VARCHARACTER","VARYING","WARNINGS","WHEN","WHERE","WITH","WRITE","XOR","YEAR_MONTH","ZEROFILL","FALSE","TRUE"]

cur_user = getpass.getuser()
cur_file = Path(__file__).stem
#default_file = "/home/"+cur_user+"/table_maker/"+cur_file+".default"
default_file = "/home/table_maker/"+cur_file+".default"
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

w1 = Label(frame1, text="Host Name: ",font=("Times",16)).pack(side="left")
hostname = default_values.readline()
e1 = Entry(frame1,width=40,font=("Times",16))
e1.insert(0,hostname.strip())
e1.pack(side="left")

w2 = Label(frame2, text="User Name: ",font=("Times",16)).pack(side="left")
username = default_values.readline()
e2 = Entry(frame2,width=40,font=("Times",16))
e2.insert(0,username.strip())
e2.pack(side="left")

key_file = "/home/table_maker/key.key"
key = ""
unciphered_passwd = ""
if os.path.isfile(key_file):
	file = open(key_file, 'rb')
	key = file.read() # The key will be type bytes
	file.close()
	cipher_suite = Fernet(key)

w3 = Label(frame3, text="Password: ",font=("Times",16)).pack(side="left")
if key != "":
	ciphered_passwd = default_values.readline()
	if ciphered_passwd != "":
		byte_ciphered_passwd = str.encode(ciphered_passwd)
		byte_unciphered_passwd = (cipher_suite.decrypt(byte_ciphered_passwd))
		unciphered_passwd = byte_unciphered_passwd.decode("utf-8")
e3 = Entry(frame3,width=40,font=("Times",16),show="*")
e3.insert(0, unciphered_passwd.strip())
e3.pack(side="left")

w4 = Label(frame4, text="Database: ",font=("Times",16)).pack(side="left")
dbase = default_values.readline()
e4 = ttk.Combobox(frame4,width=40,font=("Times",16),validate="focusout",validatecommand=lambda: check_reserved_words(dbase))
e4.insert(0, dbase.strip())
e4.pack(side="left")

btn3 = Button(framebot,text='Save Changes',font=("Times",16),command=main_program).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")
btn5 = Button(framebot,text='Test Connection',font=("Times",16),command=test_connection).pack()

default_values.close()

mw.mainloop()
