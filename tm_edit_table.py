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
import shutil
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
        elif self.get() == "":
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)

def get_file1(e1,new_window):
	file1 =  filedialog.askopenfilename(title = "Select file",filetypes = (("all files","*.*"),("csv files","*.csv")),parent=new_window)
	e1.delete(0,'end')
	e1.insert(0,file1)

def view_results(e1):
    print("View Output")
    fname = e1.get()
    if (shutil.which("cygstart") != None):
        edit_cmd = "cygstart \"" + fname + "\""
    elif (shutil.which("libreoffice") != None):
        edit_cmd = "libreoffice \"" + fname + "\""
    else:
        edit_cmd = "gedit \"" + fname + "\""
    os.system(edit_cmd)

def create_export_file(e1,new_window):
    print("Exporting Table")
    fname = e1.get()
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    if a2.get() != "":
        table_name = a2.get()
    else:
        return
    sql_cmd = "SELECT field_name,field_label,data_type,field_len,link_table,sort_order,removed FROM table_details where table_name = '"+table_name+"' order by sort_order"
    print(sql_cmd)
    header = "field_name,field_label,data_type,field_len,link_table,sort_order,removed\n"
    mycursor.execute(sql_cmd)
    fn = open(fname,"w+")
    fn.write(header)
    for row in mycursor:
        line = ",".join(map(str,row))+"\n"  # convert row to a comma delimited string
        fn.write(line)
    fn.close()
    msg_text = "Table "+table_name+" exported."
    messagebox.showwarning("Message",msg_text,parent=new_window)

def export_table():
    print("Export Table")
    parent_table = a2.get()
    child_table = a3.get()
    save_defaults(parent_table,child_table)

    new_window = Toplevel(mw)
    new_window.wm_title("Export Table Details")
    new_window.geometry('600x200+400+200')

    new_frame1 = Frame(new_window)
    new_frame2 = Frame(new_window)
    new_frame3 = Frame(new_window)
    new_frame1.pack(side=TOP,fill=X)
    new_frame2.pack(side=TOP,fill=X)
    new_frame3.pack(side=BOTTOM,fill=X)

    w1 = Label(new_frame1, text="Output File: ",font=("Times",16)).pack(side="left")
    e1 = Entry(new_frame1,width=40,font=("Times",16))
    e1.pack(side="left")
    btn1 = Button(new_frame1,text='Find',font=("Times",16),command= lambda: get_file1(e1,new_window)).pack(side="left")

    btn3 = Button(new_frame3,text='Go',font=("Times",16),command=lambda:create_export_file(e1,new_window)).pack(side="left")
    btn4 = Button(new_frame3,text='Exit',font=("Times",16),command=new_window.destroy).pack(side="right")
    btn5 = Button(new_frame3,text='View Export File',font=("Times",16),command=lambda:view_results(e1)).pack()

def import_file(e1,new_window):
    print("Importing File")
    fname = e1.get()
    if a3.get() != "":
        table_name = a3.get()
    elif a2.get() != "":
        table_name = a2.get()
    else:
        return
    clear_rows(0)
    fn = open(fname,"r")
    row_num = 0
    header = fn.readline()
    for row in fn:
        items = row.split(",")
        for i in range(0,6):
            values[row_num][i].delete(0,END)
            values[row_num][i].insert(0,items[i])
        print(row)
        row_num += 1
    fn.close()
    msg_text = "Table "+table_name+" imported."
    messagebox.showwarning("Message",msg_text,parent=new_window)

def import_table():
    print("Import Table")
    new_window = Toplevel(mw)
    new_window.wm_title("Export Table Details")
    new_window.geometry('600x200+400+200')

    new_frame1 = Frame(new_window)
    new_frame2 = Frame(new_window)
    new_frame3 = Frame(new_window)
    new_frame1.pack(side=TOP,fill=X)
    new_frame2.pack(side=TOP,fill=X)
    new_frame3.pack(side=BOTTOM,fill=X)

    w1 = Label(new_frame1, text="Input File: ",font=("Times",16)).pack(side="left")
    e1 = Entry(new_frame1,width=40,font=("Times",16))
    e1.pack(side="left")
    btn1 = Button(new_frame1,text='Find',font=("Times",16),command= lambda: get_file1(e1,new_window)).pack(side="left")

    btn3 = Button(new_frame3,text='Go',font=("Times",16),command=lambda:import_file(e1,new_window)).pack(side="left")
    btn4 = Button(new_frame3,text='Exit',font=("Times",16),command=new_window.destroy).pack(side="right")
    btn5 = Button(new_frame3,text='View File to Import',font=("Times",16),command=lambda:view_results(e1)).pack()


def confirm_delete(table_or_fields):
	new_window = Toplevel(mw)
	new_window.wm_title("Enter Credentials")
	new_window.geometry('700x200+400+200')

	new_frame1 = Frame(new_window)
	new_frame2 = Frame(new_window)
	new_frame3 = Frame(new_window)
	new_frame1.pack(side=TOP,fill=X)
	new_frame2.pack(side=TOP,fill=X)
	new_frame3.pack(side=BOTTOM,fill=X)

	label1 = Label(new_frame1, text="Username",font=("Times",16))
	label1.grid(row=0,column=0)
	user = Entry(new_frame1,width=40,font=("Times",16))
	user.grid(row=0,column=1)

	label1 = Label(new_frame2, text="Password",font=("Times",16))
	label1.grid(row=1,column=0)
	pwd = Entry(new_frame2,width=40,font=("Times",16),show="*")
	pwd.grid(row=1,column=1)

	btn = Button(new_frame3,text='Confirm Delete',font=("Times",16),command= lambda:call_delete_rtn(new_window,user,pwd,table_or_fields)).pack()

def call_delete_rtn(new_window,user,pwd,table_or_fields):
    if (pwd.get() == passwd) and (user.get() == username):
        if (table_or_fields == "Table"):
            delete_table(new_window)
        else: #(table_or_fields == "Fields")
            delete_fields(new_window)
        new_window.destroy()
    else:
        msgtxt = "Password is incorrect. "+table_or_fields+" were not deleted."
        messagebox.showwarning("Message",msgtxt,parent=new_window)
        new_window.destroy()


def delete_fields(new_window):
    print("Delete Fields")
    table_name = a2.get()
    if (a2.get() == ""):
        return
    sql_cmd = "ALTER TABLE "+table_name+" "
    sql_cmd2 = "DELETE FROM table_details WHERE (table_name='"+table_name+"') and ("
    row = 0
    drop_count = 0
    for i in removed_values:
        # if removeflag is set and the record is in the database, remove it
        if (i.get() == "1") and values[row][0].instate(['readonly']):
            drop_count += 1
            sql_cmd += "DROP COLUMN "+values[row][0].get()+","
            sql_cmd2 += " (field_name='"+values[row][0].get()+"') or"
        row += 1
    sql_cmd = sql_cmd.rstrip(",")
    sql_cmd2 = sql_cmd2.rsplit(" ",1)[0]+")"    # The rsplit will remove the last "or"
    if drop_count > 0:
        mydb = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=passwd,
                database=database_name
                )
        mycursor = mydb.cursor()
        print(sql_cmd)
        mycursor.execute(sql_cmd)
        print(sql_cmd2)
        mycursor.execute(sql_cmd2)
        mydb.commit()
        msg_text = "Table "+table_name+" had "+str(drop_count)+" fields deleted."
        messagebox.showwarning("Message",msg_text,parent=new_window)
    get_records("REFRESH")   #refresh fields


def delete_table(new_window):
    print("Delete Table")
    table_name = a2.get()
    if (a2.get() == ""):
        return
    mydb = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=passwd,
                database=database_name
                )
    mycursor = mydb.cursor()
    sql_cmd = "DROP TABLE "+table_name
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    sql_cmd = "DROP TABLE "+table_name+"_aud"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    sql_cmd = "DELETE FROM table_header WHERE table_name = '"+table_name+"'"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    sql_cmd = "DELETE FROM table_details WHERE table_name = '"+table_name+"'"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    mydb.commit()
    a2.delete(0,END)
    a3.delete(0,END)
    get_tables(database_name,table_list)
    msg_text = "Table "+table_name+" deleted."
    messagebox.showwarning("Message",msg_text,parent=new_window)

def data_table(frame4,col_widths):
    # Create and populate values array
    for i in range(0,max_rows):
               values.append([])
               add_column.append(1)
               removed_values.append("0")
               removed_values[i] = Variable()
               j = 0
               values[i].append(ttk.Entry(frame4,validate="focusout",width=col_widths[j]))
               values[i][j]['validatecommand'] = (values[i][j].register(check_reserved_words),'%P')  # validate field name
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Entry(frame4,width=col_widths[j]))  # Field label
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Combobox(frame4,validate="focusout",values=data_types,width=col_widths[j]-2)) # Data type
               values[i][j]['validatecommand'] = (values[i][j].register(check_data_type),'%P')  # validate field name
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Lotfi(frame4,width=col_widths[j]))  # Field length
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Entry(frame4,width=col_widths[j]))  # Link table
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Lotfi(frame4,width=col_widths[j]))  # Sort order
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Checkbutton(frame4,width=col_widths[j],onvalue="1",offvalue="0",variable=removed_values[i]))  # Sort order
               values[i][j].grid(row=i,  column= j)

def get_records(*args):
    if (args[0] == "PY_VAR0"): # if the value of the table changed via keystroke
        parent_table.set("")
    if (a2.get() == ""):
        if 'max_rows' in globals():
            clear_rows(0)
        return
    if (a2.get() not in table_list):
        clear_rows(0)
        a3.config(state="readonly")
        return

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT parent_table FROM table_header where table_name = '"+a2.get()+"'"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    parent_table.set(row[0])
    a3.config(state="disabled")

    sql_cmd = "SELECT field_name,field_label,data_type,field_len,link_table,sort_order,removed FROM table_details where table_name = '"+a2.get()+"' order by sort_order"
    # print(sql_cmd)
    mycursor.execute(sql_cmd)
    i = 0
    for row in mycursor:
        j = 0
        values[i][j].config(state=NORMAL) # you cant insert or delete in readonly mode
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        values[i][j].config(state="readonly")
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        j += 1
        values[i][j].config(state=NORMAL) # you cant insert or delete in readonly mode
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        values[i][j].config(state="disabled")
        j += 1
        tempstr = row[j]
        if row[j] == None:
            tempstr = ""
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        values[i][j].insert(0,tempstr)
        values[i][j].config(state="readonly")
        j += 1
        tempstr = row[j]
        if row[j] == None:
            tempstr = ""
        values[i][j].delete(0,END)
        values[i][j].insert(0,tempstr)
        j += 1
        tempstr = row[j]
        if row[j] == None:
            tempstr = ""
        values[i][j].delete(0,END)
        values[i][j].insert(0,tempstr)
        j += 1
        values[i][j].deselect()
        if (row[j] == 1):
            values[i][j].select()

        add_column[i] = 0    # dont add column if already exists
        i += 1
    clear_rows(i) # Clear our remaining rows


def clear_rows(start_row):
    # Clear out remaining rows
    for i in range(start_row,max_rows):
        j = 0
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].deselect()

        add_column[i] = 1



def save_defaults(*args):
	default_values = open(default_file,"w+")
	for x in args:
		default_values.write(x+"\n")
	default_values.close()


def main_program():
    table_name = a2.get()
    parent_table = a3.get()
    save_defaults(table_name,parent_table)

    if table_name == "":
        return

    a3.config(state="disabled")

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()

    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_cmd = "SELECT identifier FROM table_header WHERE table_name = '"+table_name+"'"
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if (row == None):
        sql_cmd = "INSERT INTO table_header (table_name,modified_by,modified_on,parent_table) VALUES ('"
        sql_cmd += table_name+"','"+getpass.getuser()+"','"+cur_time+"','"+parent_table+"')"
    else:
        sql_cmd = "UPDATE table_header SET modified_by='"+getpass.getuser()+"',modified_on='"+cur_time+"',parent_table='"+parent_table+"' WHERE table_name ='"+table_name+"'"
    print(sql_cmd)
    mycursor.execute(sql_cmd)

    sql_cmd = "CREATE TABLE IF NOT EXISTS "+table_name
    sql_cmd += " (identifier integer AUTO_INCREMENT PRIMARY KEY,"
    sql_cmd += "modified_by varchar(50),"
    sql_cmd += "modified_on datetime,"
    sql_cmd += "removed boolean default 0,"

    sql_cmd2 = "CREATE TABLE IF NOT EXISTS "+table_name+"_aud"
    sql_cmd2 += " (identifier integer,"
    sql_cmd2 += "modified_by varchar(50),"
    sql_cmd2 += "modified_on datetime,"
    sql_cmd2 += "removed boolean default 0,"

    if (parent_table == ""):
        sql_cmd += "template_id integer)"
        sql_cmd2 += "template_id integer)"
    else:
        sql_cmd += "template_id integer,"
        sql_cmd += parent_table+" integer)"
        sql_cmd2 += "template_id integer,"
        sql_cmd2 += parent_table+" integer)"

    print(sql_cmd)
    mycursor.execute(sql_cmd)
    print(sql_cmd2)
    mycursor.execute(sql_cmd2)
    mydb.commit()

    sql_cmd = "ALTER TABLE "+table_name+" "
    sql_cmd2 = "ALTER TABLE "+table_name+"_aud "
    i = 0;
    field_name = values[i][0].get()
    field_label = values[i][1].get()
    data_type = values[i][2].get()
    data_type = data_type.upper()
    field_len = values[i][3].get()
    link_table = values[i][4].get()
    sort_order = values[i][5].get()
    removed_flag = removed_values[i].get()
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    while (field_name != "") and (i < max_rows):
            if add_column[i] == 1:
                sql_cmd += "ADD COLUMN "
                sql_cmd2 += "ADD COLUMN "
                if (data_type == "VARCHAR") or (data_type == "varchar"):
                    sql_cmd += field_name+" "+data_type+"("+field_len+"),"
                    sql_cmd2 += field_name+" "+data_type+"("+field_len+"),"
                else:
                    sql_cmd += field_name+" "+data_type+","
                    sql_cmd2 += field_name+" "+data_type+","

                if (field_len == ""):
                    field_len = "NULL"
                if (sort_order == ""):
                    sort_order = "NULL"
                sql_cmd3 = "INSERT INTO table_details (table_name,modified_by,modified_on,field_name,field_label,data_type,field_len,link_table,sort_order,parent_table,removed) VALUES ('"
                sql_cmd3 += table_name+"','"+getpass.getuser()+"','"+cur_time+"','"+field_name+"','"+field_label+"','"+data_type+"',"+field_len+",'"+link_table+"',"+sort_order+",'"+parent_table+"',"+removed_flag+")"
                print(sql_cmd3)
                mycursor.execute(sql_cmd3)

                values[i][0].configure(state="readonly")    # field Name
                values[i][2].configure(state="disabled")    # data type
                values[i][3].configure(state="readonly")    # field length
                add_column[i] = 0
            else:
                if (sort_order == ""):
                    sort_order = "NULL"
                sql_cmd4 = "UPDATE table_details SET modified_by='"+getpass.getuser()+"',modified_on='"+cur_time+"',field_label='"+field_label+"',link_table='"+link_table+"',sort_order="+sort_order+",parent_table='"+parent_table+"',removed='"+removed_flag+"' "
                sql_cmd4 += "WHERE (table_name='"+table_name+"') and (field_name='"+field_name+"')"
                print(sql_cmd4)
                mycursor.execute(sql_cmd4)

            i += 1
            field_name = values[i][0].get()
            field_label = values[i][1].get()
            data_type = values[i][2].get()
            data_type = data_type.upper()
            field_len = values[i][3].get()
            link_table = values[i][4].get()
            sort_order = values[i][5].get()
            removed_flag = removed_values[i].get()

    sql_cmd = sql_cmd.rstrip(",")
    print(sql_cmd)
    mycursor.execute(sql_cmd)

    sql_cmd2 = sql_cmd2.rstrip(",")
    print(sql_cmd2)
    mycursor.execute(sql_cmd2)

    mydb.commit()
    get_tables(database_name,table_list)
    msg_text = "Table Created/Updated: "+table_name
    messagebox.showinfo("Information",msg_text)
    print("Finished\n")

def get_tables(database_name,table_list):
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
    table_list.clear()
    for x in mycursor:
        table_list.append(x[0])
    a2['values']=table_list
    a3['values']=table_list

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=900,height=350)

def check_reserved_words(str_value):
    if str_value.upper() in reserved_words:
            msg_text = "Invalid field or table name: "+str_value
            messagebox.showerror("Error",msg_text)
            return(False)
    return(True)

def check_data_type(str_value):
    if str_value == "":
        return(True)
    elif str_value.upper() not in data_types:
        msg_text = "Invalid data type: "+str_value
        messagebox.showerror("Error",msg_text)
        return(False)
    return(True)

# Start the main program here
if __name__ == "__main__":
    current_file = Path(__file__).stem
    mw=Tk()
    mw.geometry('900x500+200+150')
    mw.title(current_file)

    # MySQL reserved words. These words cannot be used for table or field names
    reserved_words = ["ANALYZE","AND","AS","ASC","AUTO_INCREMENT","BDB","BERKELEYDB","BETWEEN","BIGINT","BINARY","BLOB","BOTH","BTREE","BY","CASCADE","CASE","CHANGE","CHAR","CHARACTER","CHECK","COLLATE","COLUMN","COLUMNS","CONSTRAINT","CREATE","CROSS","CURRENT_DATE","CURRENT_TIME","CURRENT_TIMESTAMP","DATABASE","DATABASES","DAY_HOUR","DAY_MINUTE","DAY_SECOND","DEC","DECIMAL","DEFAULT","DELAYED","DELETE","DESC","DESCRIBE","DISTINCT","DISTINCTROW","DIV","DOUBLE","DROP","ELSE","ENCLOSED","ERRORS","ESCAPED","EXISTS","EXPLAIN","FIELDS","FLOAT","FOR","FORCE","FOREIGN","FROM","FULLTEXT","FUNCTION","GEOMETRY","GRANT","GROUP","HASH","HAVING","HELP","HIGH_PRIORITY","HOUR_MINUTE","HOUR_SECOND","IF","IGNORE","IN","INDEX","INFILE","INNER","INNODB","INSERT","INT","INTEGER","INTERVAL","INTO","IS","JOIN","KEY","KEYS","KILL","LEADING","LEFT","LIKE","LIMIT","LINES","LOAD","LOCALTIME","LOCALTIMESTAMP","LOCK","LONG","LONGBLOB","LONGTEXT","LOW_PRIORITY","MASTER_SERVER_ID","MATCH","MEDIUMBLOB","MEDIUMINT","MEDIUMTEXT","MIDDLEINT","MINUTE_SECOND","MOD","MRG_MYISAM","NATURAL","NOT","NULL","NUMERIC","ON","OPTIMIZE","OPTION","OPTIONALLY","OR","ORDER","OUTER","OUTFILE","PRECISION","PRIMARY","PRIVILEGES","PROCEDURE","PURGE","READ","REAL","REFERENCES","REGEXP","RENAME","REPLACE","REQUIRE","RESTRICT","RETURNS","REVOKE","RIGHT","RLIKE","RTREE","SELECT","SET","SHOW","SMALLINT","SOME","SONAME","SPATIAL","SQL_BIG_RESULT","SQL_CALC_FOUND_ROWS","SQL_SMALL_RESULT","SSL","STARTING","STRAIGHT_JOIN","STRIPED","TABLE","TABLES","TERMINATED","THEN","TINYBLOB","TINYINT","TINYTEXT","TO","TRAILING","TYPES","UNION","UNIQUE","UNLOCK","UNSIGNED","UPDATE","USAGE","USE","USER_RESOURCES","USING","VALUES","VARBINARY","VARCHAR","VARCHARACTER","VARYING","WARNINGS","WHEN","WHERE","WITH","WRITE","XOR","YEAR_MONTH","ZEROFILL","FALSE","TRUE"]

    default_file = expanduser("~")+"/table_maker/"+current_file+".default"
    # If file does not exist, create one
    if not os.path.isfile(default_file):
    		cmd = "touch " + default_file
    		os.system(cmd)
    default_values = open(default_file,"r")

    frame1 = Frame(mw)
    frame2 = Frame(mw)
    frame3 = Frame(mw)
    frame4 = Frame(mw)
    frame5 = Frame(mw)
    framebot = Frame(mw)
    frame1.pack(side=TOP,fill=X)
    frame2.pack(side=TOP,fill=X)
    frame3.pack(side=TOP,fill=X)
    frame4.pack(side=TOP,fill=X)
    frame5.pack(side=TOP,fill=X)
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

    w2 = Label(frame2, text="Table Name: ",font=("Times",16)).pack(side="left")
    table_name = StringVar()
    tempvar = default_values.readline()
    table_name.set(tempvar.strip())
    table_name.trace('w',get_records)
    a2 = ttk.Combobox(frame2,width=40,font=("Times",16),textvar=table_name,validate="focusout",validatecommand=lambda: check_reserved_words(table_name.get()))
    a2.pack(side="left")

    w3 = Label(frame3, text="Parent Table: ",font=("Times",16)).pack(side="left")
    parent_table = StringVar()
    tempvar = default_values.readline()
    parent_table.set(tempvar.strip())
    a3 = ttk.Combobox(frame3,width=40,font=("Times",16),textvar=parent_table,state="disabled")
    a3.pack(side="left")

    headers = ["Field Name","Field Label","Data Type","Length","Link Table","Sort Order","Remove"]
    col_widths = [20,20,12,8,20,8,6]
    column = 0
    for header in headers:
        l1 = Entry(frame4,relief=FLAT,width=col_widths[column])
        l1.insert(0,header)
        l1.config(state="readonly")
        l1.grid(row=0,column= column)
        column += 1

    table_list = []
    get_tables(database_name,table_list)

    btn1 = Button(framebot,text='Create/Update Table',font=("Times",16),command=main_program).pack(side="left")
    btn2 = Button(framebot,text='Delete Fields',font=("Times",16),command=lambda:confirm_delete("Fields")).pack(side="left")
    btn3 = Button(framebot,text='Delete Table',font=("Times",16),command=lambda:confirm_delete("Table")).pack(side="left")
    btn4 = Button(framebot,text='Export Table Info',font=("Times",16),command=export_table).pack(side="left")
    btn5 = Button(framebot,text='Import Table Info',font=("Times",16),command=import_table).pack(side="left")
    btn6 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")

    default_values.close()

    canvas=Canvas(frame5)
    frame=Frame(canvas)
    myscrollbar=Scrollbar(frame5,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",myfunction)

    values = []
    add_column = []
    removed_values = []
    max_rows = 20
    data_types=["VARCHAR","INT","DATE","FLOAT","BOOLEAN"]
    data_table(frame,col_widths)
    get_records("INIT")

    mw.mainloop()
