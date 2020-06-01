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

def get_dropdown(source,record_list,mydb):
    mycursor = mydb.cursor()
    dot_pos = source.find(".")
    table_name = source[0:dot_pos]
    field_name = source[dot_pos+1:len(source)]
    sql_cmd = "SELECT "+field_name+" FROM "+table_name+" WHERE removed = 0"
    mycursor.execute(sql_cmd)
    for x in mycursor:
        record_list.append(x[0])

def get_field_details(table_name,field_names,field_labels,data_types,link_tables):
	mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=database_name
        )
	# Get field names and their data types
	mycursor = mydb.cursor(buffered=True)
	sql_cmd = "select field_name,field_label,data_type,field_len,link_table,sort_order,parent_table from table_details where (table_name = '"+table_name+"') and (removed='0') order by sort_order"
	mycursor.execute(sql_cmd)
	field_names.clear()
	field_labels.clear()
	data_types.clear()
	link_tables.clear()
	for x in mycursor:
		field_names.append(x[0])
		field_labels[x[0]] = x[1]
		data_types[x[0]] = x[2]
		dropdown_values = []
		if (x[4] != "") and (x[4] != None):
			get_dropdown(x[4],dropdown_values,mydb)
		link_tables[x[0]] = dropdown_values
	for i in range(max_rows):
		values[i][0]["values"] = field_names
	return(True)

def set_input(event,values,orig_values,field_labels,data_types,link_tables,col_width):
    widget = event.widget
    row_pos = event.widget.grid_info()["row"]
    print("setting input for row "+str(row_pos))
    field = event.widget.get()
    if (field != orig_values[row_pos]):
        orig_values[row_pos] = field
        values[row_pos][1].delete(0,END)
        if (field == ""):
            values[row_pos][2] = Entry(frame,width=col_width)
        elif (data_types[field] == "VARCHAR"):
            values[row_pos][1].insert(0,field_labels[field])
            if len(link_tables[field]) == 0:
                values[row_pos][2] = Entry(frame,width=col_width)
            else:
                values[row_pos][2] = ttk.Combobox(frame,width=col_width-2,values=link_tables[field])
        elif (data_types[field] == "INT"):
            values[row_pos][1].insert(0,field_labels[field])
            values[row_pos][2] = Lotfi(frame,width=col_width)
        elif (data_types[field] == "FLOAT"):
            values[row_pos][1].insert(0,field_labels[field])
            values[row_pos][2] = Lotfi(frame,width=col_width)
        elif (data_types[field] == "DATE"):
            values[row_pos][1].insert(0,field_labels[field])
            values[row_pos][2] = DateEntry(frame,width=col_width-2,date_pattern="Y-mm-dd")
        else:
            values[row_pos][1].insert(0,field_labels[field])
            values[row_pos][2] = Entry(frame,width=col_width)
        values[row_pos][2].grid(row=row_pos,column=2)
    return(True)

def data_table(frame4,col_widths):
    # Create and populate values array
    for i in range(0,max_rows):
               values.append([])
               j = 0
               values[i].append(ttk.Combobox(frame4,width=col_widths[j]-2)) # Field name
               values[i][j].bind("<<ComboboxSelected>>",lambda event:set_input(event,values,orig_values,field_labels,data_types,link_tables,col_widths[2]))
               orig_values.append("")
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Entry(frame4,width=col_widths[j]))  # Field label
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Entry(frame4,width=col_widths[j]))  # default value
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Checkbutton(frame4,width=col_widths[j],onvalue=1,offvalue=0))  # readonly
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Checkbutton(frame4,width=col_widths[j],onvalue=1,offvalue=0))  # copy
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Checkbutton(frame4,width=col_widths[j],onvalue=1,offvalue=0))  # mandatory
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Lotfi(frame4,width=col_widths[j]))  # Sort order
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Checkbutton(frame4,width=col_widths[j],onvalue=1,offvalue=0))  # removed
               values[i][j].grid(row=i,  column= j)

def confirm_delete(template_or_fields):
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

	btn = Button(new_frame3,text='Confirm Delete',font=("Times",16),command= lambda:call_delete_rtn(new_window,user,pwd,template_or_fields)).pack()

def call_delete_rtn(new_window,user,pwd,template_or_fields):
    if (pwd.get() == passwd) and (user.get() == username):
        if (template_or_fields == "Template"):
            delete_template(new_window)
        else: #(table_or_fields == "Fields")
            delete_fields(new_window)
        new_window.destroy()
    else:
        msgtxt = "Password is incorrect. "+template_or_fields+" were not deleted."
        messagebox.showwarning("Message",msgtxt,parent=new_window)
        new_window.destroy()


def delete_fields(new_window):
    print("Delete Fields")
    table_name = a2.get()
    template_name = a3.get()
    if (table_name == "") or (template_name == ""):
        return

    mydb = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=passwd,
                database=database_name
                )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier FROM template_header WHERE (name = '"+template_name+"') and (table_name = '"+table_name+"')"
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    template_id = row[0]

    sql_cmd = "DELETE FROM template_details WHERE (template_header = "+str(template_id)+") AND (removed = 1)"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    mydb.commit()
    msg_text = "Fields marked as removed were deleted."
    messagebox.showwarning("Message",msg_text,parent=new_window)
    get_records("REFRESH")   #refresh fields


def delete_template(new_window):
    print("Delete Template")
    table_name = a2.get()
    template_name = a3.get()
    if (table_name == "") or (template_name == ""):
        return
    mydb = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=passwd,
                database=database_name
                )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier FROM template_header WHERE (name = '"+template_name+"') and (table_name = '"+table_name+"')"
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    template_id = row[0]
    sql_cmd = "DELETE FROM template_details WHERE template_header = "+str(template_id)
    print(sql_cmd)
    mycursor.execute(sql_cmd)

    sql_cmd = "DELETE FROM template_header WHERE identifier = "+str(template_id)
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    mydb.commit()

    a3.delete(0,END)
    get_templates("RELOAD",template_list)   # Update template list
    clear_rows(0)

    msg_text = "Template "+template_name+" deleted."
    messagebox.showwarning("Message",msg_text,parent=new_window)

def get_records(*args):
    #if (args[0] == "PY_VAR1"): # if the value of the template changed via keystroke
    if (a3.get() not in template_list):
        clear_rows(0)
        return

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    if (a2.get() != "") and (a3.get() != ""):
        sql_cmd = "SELECT identifier FROM template_header WHERE (table_name = '"+a2.get()+"') and (name = '"+a3.get()+"')"
        print(sql_cmd)
        mycursor.execute(sql_cmd)
        row = mycursor.fetchone()
        if row != None:
            sql_cmd = "SELECT field_name,field_label,def_value,disp,copy,mand,sort_order,removed FROM template_details where template_header = '"+str(row[0])+"' order by sort_order"
        else:
            return
    else:
        return
    # print(sql_cmd)
    mycursor.execute(sql_cmd)
    i = 0
    for row in mycursor:
        j = 0
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        orig_values[i] = row[j]
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])

        j += 1
        field = row[0]
        if (data_types[field] == "VARCHAR"):
            if len(link_tables[field]) == 0:
                values[i][j] = Entry(frame,width=col_widths[j])
            else:
                values[i][j] = ttk.Combobox(frame,width=col_widths[j]-2,values=link_tables[field])
            values[i][j].insert(0,row[j])
        elif (data_types[field] == "INT"):
            values[i][j].insert(0,row[j])
            values[i][j] = Lotfi(frame,width=col_widths[j])
        elif (data_types[field] == "FLOAT"):
            values[i][j] = Lotfi(frame,width=col_widths[j])
            values[i][j].insert(0,row[j])
        elif (data_types[field] == "DATE"):
            values[i][j] = DateEntry(frame,width=col_widths[j]-2,date_pattern="Y-mm-dd")
            values[i][j].configure(validate="none")
            values[i][j].delete(0,END)
            if (row[j] != ""):
                values[i][j].insert(0,row[j])
        else:
            values[i][j] = Entry(frame,width=col_widths[j])
            values[i][j].insert(0,row[j])
        values[i][j].grid(row=i,column=j)

        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])
        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])
        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])
        j += 1
        tempstr = row[j]
        if row[j] == None:
            tempstr = ""
        values[i][j].delete(0,END)
        values[i][j].insert(0,tempstr)
        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])

        i += 1
    clear_rows(i) # Clear our remaining rows


def clear_rows(start_row):
    # Clear out remaining rows
    for i in range(start_row,max_rows):
        j = 0
        values[i][j].delete(0,END)
        orig_values[i] = ""
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].state(["!selected"])
        j += 1
        values[i][j].state(["!selected"])
        j += 1
        values[i][j].state(["!selected"])
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].state(["!selected"])

def load_all_fields(*args):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    if a2.get() == "":
        return

    sql_cmd = "SELECT field_name,field_label,'',0,0,0,sort_order,0 FROM table_details where table_name='"+a2.get()+"' order by sort_order"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    i = 0
    for row in mycursor:
        j = 0
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        orig_values[i] = row[j]
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])

        j += 1
        field = row[0]
        if (data_types[field] == "VARCHAR"):
            if len(link_tables[field]) == 0:
                values[i][j] = Entry(frame,width=col_widths[j])
            else:
                values[i][j] = ttk.Combobox(frame,width=col_widths[j]-2,values=link_tables[field])
            values[i][j].insert(0,row[j])
        elif (data_types[field] == "INT"):
            values[i][j] = Lotfi(frame,width=col_widths[j])
            values[i][j].insert(0,row[j])
        elif (data_types[field] == "FLOAT"):
            values[i][j] = Lotfi(frame,width=col_widths[j])
            values[i][j].insert(0,row[j])
        elif (data_types[field] == "DATE"):
            values[i][j] = DateEntry(frame,width=col_widths[j]-2,date_pattern="Y-mm-dd")
            values[i][j].configure(validate="none")
            values[i][j].delete(0,END)
            if row[j] != "":
                values[i][j].insert(0,row[j])
        else:
            values[i][j] = Entry(frame,width=col_widths[j])
            values[i][j].insert(0,row[j])
        values[i][j].grid(row=i,column=j)

        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])
        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])
        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])
        j += 1
        tempstr = row[j]
        if row[j] == None:
            tempstr = ""
        values[i][j].delete(0,END)
        values[i][j].insert(0,tempstr)
        j += 1
        temp_value = row[j]
        if (temp_value == None) or (temp_value == 0):
            values[i][j].state(["!selected"])
        else:
            values[i][j].state(["selected"])

        i += 1
    clear_rows(i) # Clear our remaining rows

def save_defaults(table_name,template_name):
	default_values = open(default_file,"w+")
	default_values.write(table_name+"\n")
	default_values.write(template_name+"\n")
	default_values.close()


def save_template(template_list):
    parent_table = a2.get()
    template_name = a3.get()
    if parent_table == "":
        msg_text = "Error: You must enter a Table Name"
        messagebox.showerror("Error",msg_text)
        return
    if (template_name == ""):
        msg_text = "Error: You must enter a Template Name"
        messagebox.showerror("Error",msg_text)
        return
    save_defaults(parent_table,template_name)

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier,removed FROM template_header WHERE name = '"+template_name+"'"
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if row == None: # template does not exist, create everythin new
        now = datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        sql_cmd = "INSERT INTO template_header (modified_by,modified_on,name,table_name) VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"','"+template_name+"','"+parent_table+"')"
        print(sql_cmd)
        mycursor.execute(sql_cmd)
        last_row = mycursor.lastrowid
        template_header_id = last_row
        for i in range(max_rows):
            field_name = values[i][0].get()
            if field_name != "":
                field_label = values[i][1].get()
                disp = "0"
                entr = "0"
                cpy = "0"
                mand = "0"
                remv = "0"
                if values[i][3].instate(['selected']):
                    disp = "1"
                if values[i][4].instate(['selected']):
                    cpy = "1"
                if values[i][5].instate(['selected']):
                    mand = "1"
                if values[i][7].instate(['selected']):
                    remv = "1"
                def_val = values[i][2].get()
                sort_order = "Null"
                if values[i][6].get() != "":
                    sort_order = values[i][6].get()
                sql_cmd = "INSERT INTO template_details (modified_by,modified_on,template_header,field_name,field_label,def_value,disp,ent,copy,mand,removed,sort_order) VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"',"+str(last_row)+",'"+field_name+"','"+field_label+"','"+def_val+"',"+disp+","+entr+","+cpy+","+mand+","+remv+","+str(sort_order)+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
        mydb.commit()

        temp_file = "/home/table_maker/template_actions/"+database_name+"-"+parent_table+"-"+str(template_header_id)+".py"
        empty_file = "/home/table_maker/template_actions/template.txt"
        if not os.path.isfile(temp_file):
            cmd = "cp "+empty_file+" \""+temp_file+"\""
            print(cmd)
            os.system(cmd)
    else:
        template_header_id = row[0]
        removed = row[1]
        sql_cmd = "UPDATE template_header SET descr = '',num = 0,removed=0 "
        if removed == 1:
            msg_text = "Template is currently removed but will be restored."
            messagebox.showinfo("Information",msg_text)
        sql_cmd += " WHERE identifier = "+str(template_header_id)
        mycursor.execute(sql_cmd)
        sql_cmd = "SELECT identifier FROM template_details WHERE template_header = "+str(template_header_id)+" ORDER BY identifier"
        mycursor.execute(sql_cmd)
        row_count = 0
        identifiers = []
        for row in mycursor:
            identifiers.append(row[0])
            row_count += 1
        now = datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        for i in range(max_rows):
            disp = "0"
            entr = "0"
            cpy = "0"
            mand = "0"
            remv = "0"
            if values[i][3].instate(['selected']):
                disp = "1"
            if values[i][4].instate(['selected']):
                cpy = "1"
            if values[i][5].instate(['selected']):
                mand = "1"
            if values[i][7].instate(['selected']):
                remv = "1"
            def_val = values[i][2].get()
            sort_order = values[i][6].get()
            if sort_order == "":
                sort_order = "Null"
            if (values[i][0].get() != "") and (i < row_count):
                sql_cmd = "UPDATE template_details SET modified_by = '"+getpass.getuser()+"',modified_on='"+str(cur_time)+"',"
                sql_cmd += "field_name='"+values[i][0].get()+"',field_label='"+values[i][1].get()+"',def_value='"+def_val+"',disp="+disp+",copy="+cpy+",mand="+mand+",removed="+remv+",sort_order="+sort_order
                sql_cmd += " WHERE (template_header="+str(template_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (values[i][0].get() != "") and (i >= row_count):
                sql_cmd = "INSERT INTO template_details (modified_by,modified_on,template_header,field_name,field_label,def_value,disp,copy,mand,removed,sort_order) "
                sql_cmd += "VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"',"+str(template_header_id)+",'"+values[i][0].get()+"','"+values[i][1].get()+"','"+def_val+"',"+disp+","+cpy+","+mand+","+remv+","+sort_order+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (values[i][0].get() == "") and (i < row_count):
                sql_cmd = "DELETE FROM template_details WHERE (template_header="+str(template_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
        mydb.commit()

    get_templates("RELOAD",template_list)

    msg_text = "Template Saved."
    messagebox.showinfo("Information",msg_text)

def get_tables(*args):
    print("database "+database_name)
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=database_name
        )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT DISTINCT table_name FROM table_details WHERE (table_name NOT LIKE '%_aud') ORDER BY table_name"
    mycursor.execute(sql_cmd)
    table_list = []
    for x in mycursor:
        table_list.append(x[0])
    a2['values']=table_list
    if 'max_rows' in globals(): # If called first time, don't clear out parent and child tables
        parent_table.set("")
        template_name.set("")

def get_templates(event,template_list):
    print("database "+database_name)
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    parent_table = a2.get()
    mycursor.execute("select name from template_header where table_name = '"+parent_table+"'")
    template_list.clear()
    for x in mycursor:
        template_list.append(x[0])
    a3['values']=template_list
    if (event != "INIT") and (event != "RELOAD"):   # A new table was selected so clear out template name
        template_name.set("")
        clear_rows(0)

def edit_actions():
    table_name = a2.get()
    template_name = a3.get()
    if (table_name == "") or (template_name ==""):
        return
    save_defaults(table_name,template_name)
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier FROM template_header WHERE (name = '"+template_name+"') AND (table_name = '"+table_name+"')"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    table_name = a2.get()
    if row == None:
        return
    template_id = row[0]
    temp_file = "/home/table_maker/template_actions/"+database_name+"-"+table_name+"-"+str(template_id)+".py"
    if (shutil.which("cygstart") != None):
        edit_cmd = "cygstart \"" + temp_file + "\""
    elif (shutil.which("atom") != None):
        edit_cmd = "atom \"" + temp_file + "\""
    else:
        edit_cmd = "gedit \"" + temp_file + "\""
    os.system(edit_cmd)

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=1000,height=350)

# Start the main program here
if __name__ == "__main__":
    current_file = Path(__file__).stem
    mw=Tk()
    mw.geometry('1000x500+200+150')
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


    w2 = Label(frame1, text="Table Name: ",font=("Times",16)).pack(side="left")
    parent_table = StringVar()
    tempvar = default_values.readline()
    parent_table.set(tempvar.strip())
    a2 = ttk.Combobox(frame1,width=40,font=("Times",16),textvar=parent_table,state="readonly",validate="focusout",validatecommand=lambda: get_field_details(parent_table.get(),field_names,field_labels,data_types,link_tables))
    a2.bind("<<ComboboxSelected>>",lambda event:get_templates(event,template_list))
    a2.pack(side="left")

    w3 = Label(frame2, text="Template Name: ",font=("Times",16)).pack(side="left")
    template_name = StringVar()
    tempvar = default_values.readline()
    template_name.set(tempvar.strip())
    template_name.trace('w',get_records)
    a3 = ttk.Combobox(frame2,width=40,font=("Times",16),textvar=template_name)
    a3.pack(side="left")

    headers = ["Field Name","Field Label","Default Value","ReadOnly","Copy","Mandatory","Sort Order","Remove"]
    col_widths = [20,20,20,8,8,8,10,6]
    column = 0
    for header in headers:
        l1 = Entry(frame4,relief=FLAT,width=col_widths[column])
        l1.insert(0,header)
        l1.config(state="readonly")
        l1.grid(row=0,column= column)
        column += 1

    get_tables(database_name)
    template_list = []
    if (a2.get() != ""):
        get_templates("INIT",template_list)

    btn1 = Button(framebot,text='Save Template',font=("Times",16),command=lambda:save_template(template_list)).pack(side="left")
    btn2 = Button(framebot,text='Delete Fields',font=("Times",16),command=lambda:confirm_delete("Fields")).pack(side="left")
    btn2 = Button(framebot,text='Delete Template',font=("Times",16),command=lambda:confirm_delete("Template")).pack(side="left")
    btn3 = Button(framebot,text='Edit Actions',font=("Times",16),command=edit_actions).pack(side="left")
    btn4 = Button(framebot,text='Load All Fields',font=("Times",16),command=load_all_fields).pack(side="left")
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
    orig_values = []
    max_rows = 20
    data_table(frame,col_widths)

    field_names = []
    field_names.append("")
    field_labels = {}
    data_types = {}
    link_tables = {}
    if a2.get() != "":
        get_field_details(parent_table.get(),field_names,field_labels,data_types,link_tables)

    get_records("INIT")

    mw.mainloop()
