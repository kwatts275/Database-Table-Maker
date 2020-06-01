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


def execute_query(parent_tables,field_names,field_labels,values,max_rows,data_types,column_values,removed_values):
    parent_table = a2.get()
    query_name = a3.get()
    query_desc = a4.get()
    if parent_table == "":
        msg_text = "Error: You must enter a Table Name"
        messagebox.showerror("Error",msg_text)
        return
    if (query_name == ""):
        msg_text = "Error: You must enter a Query Name"
        messagebox.showerror("Error",msg_text)
        return
    save_defaults(parent_table,query_name,query_desc)

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier,sql_command FROM query_header WHERE (query_name = '"+a3.get()+"') and (table_name = '"+a2.get()+"')"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if (row == None):
        msg_text = "Error: You must save query before executing."
        messagebox.showerror("Error",msg_text)
        return
    query_header_id = row[0]
    sql_query = row[1]
    sql_cmd = "SELECT field_name,field_label FROM query_columns WHERE (query_header='"+str(query_header_id)+"') ORDER BY sort_order"
    mycursor.execute(sql_cmd)

    query_labels = []
    row_count = 0
    for row in mycursor:
        query_labels.append(row[1])
        row_count += 1
    if row_count == 0:
        msg_txt = "No columns selected!"
        messagebox.showerror("Error",msg_txt)
        return

    print(sql_query)
    try:
        mycursor.execute(sql_query)
    except mysql.connector.Error as e:
        msg_text = "Error in SQL syntax. Error number "+str(e.errno)
        messagebox.showerror("Error",msg_text)
        return

    temp_file = expanduser("~")+"/table_maker/"+current_file+"_"+a3.get()+".csv"

    tf = open(temp_file,"w+")
    headers = ",".join(query_labels)
    tf.write(headers+"\n")
    for row in mycursor:
        output_line = ""
        for i in range(0,len(row)):
            output_line += str(row[i]).strip()+","
        tf.write(output_line+"\n")
    tf.close()
    msg_text = "SQL query complete"
    messagebox.showinfo("Info",msg_text)

def view_results():
    temp_file = expanduser("~")+"/table_maker/"+current_file+"_"+a3.get()+".csv"
    if (shutil.which("cygstart") != None):
        edit_cmd = "cygstart \"" + temp_file + "\""
    elif (shutil.which("libreoffice") != None):
        edit_cmd = "libreoffice \"" + temp_file + "\""
    else:
        edit_cmd = "gedit \"" + temp_file + "\""
    os.system(edit_cmd)


def data_table(frame,col_widths):
    # Create and populate values array
	operators=["=","!=","like",">",">=","<","<="]
	and_or=["AND","OR"]

	for i in range(0,max_rows):
               values.append([])
               add_column.append(1)
               j = 0
               values[i].append(Entry(frame,width=col_widths[j],show="(",justify="right")) #left paren
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Combobox(frame,values=field_labels,width=col_widths[j]-2,state="readonly"))
               # When a field from the combobox is selected, set the dropdown for the field values
               values[i][j].bind("<<ComboboxSelected>>",lambda event:set_input(event,frame,values,orig_values,data_types,link_tables,30))
               orig_values.append("")
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Combobox(frame,values=operators,width=col_widths[j]-2))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Entry(frame,width=col_widths[j]))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Entry(frame,width=col_widths[j],show=")"))  # right paren
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Combobox(frame,values=and_or,width=col_widths[j]-2))
               values[i][j].set("AND")   # set default value to AND
               values[i][j].grid(row=i,  column= j)


def get_records(*args):
    if (a2.get() == ""):    # If table name is blank, clear out records
        if 'max_rows' in globals():
            clear_rows(0)
        return
    if a3.get() == "":      # If query name is blank, clear out recordsa
        return

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier,query_description FROM query_header WHERE (query_name = '"+a3.get()+"') and (table_name = '"+a2.get()+"')"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if (row == None):
        query_desc.set("")
        clear_rows(0) # Clear our remaining rows
        return
    query_header = row[0]
    query_desc.set(row[1])

    sql_cmd = "SELECT left_paren,field_name,operator,field_value,right_paren,and_or FROM query_details WHERE query_header = "+str(query_header)+" ORDER BY identifier"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    i = 0
    for row in mycursor:
        j = 0
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        values[i][j].config(values=field_labels)
        values[i][j].config(state="readonly")
        orig_values[i] = row[j]
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        j += 1
        values[i][j].delete(0,END)
        if (row[1] not in link_tables):
            values[i][j].insert(0,row[j])
        elif len(link_tables[row[1]]) == 0:
            values[i][j].insert(0,row[j])
        else: #if there is a link table, redefine values as a combobox
            values[i][j] = ttk.Combobox(frame,width=28,values=link_tables[row[1]])
            values[i][j].insert(0,row[j])
            values[i][j].grid(row=i,column=j)
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])

        add_column[i] = 0    # dont add column if already exists
        i += 1
    clear_rows(i) # Clear our remaining rows


def clear_rows(start_row):
    # Clear out remaining rows
    for i in range(start_row,max_rows):
        orig_values[i] = ""
        j = 0
        values[i][j].delete(0,END)
        j += 1
        values[i][j].config(state=NORMAL)
        values[i][j].delete(0,END)
        values[i][j].config(values=field_labels)
        values[i][j].config(state="readonly")
        j += 1
        values[i][j].delete(0,END)
        j += 1
        #values[i][j].delete(0,END)
        values[i][j] = Entry(frame,width =30)
        values[i][j].grid(row=i,column=j)
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].delete(0,END)
        values[i][j].insert(0,"AND")

        add_column[i] = 1



def save_defaults(table_name,query_name,query_desc):
	default_values = open(default_file,"w+")
	default_values.write(table_name+"\n")
	default_values.write(query_name+"\n")
	default_values.write(query_desc+"\n")
	default_values.close()

def get_dropdown(source,record_list,mydb):
    mycursor = mydb.cursor()
    dot_pos = source.find(".")
    table_name = source[0:dot_pos]
    field_name = source[dot_pos+1:len(source)]
    if table_name not in table_list:
        return
    sql_cmd = "select "+field_name+" from "+table_name
    mycursor.execute(sql_cmd)
    for x in mycursor:
        record_list.append(x[0])

def validate_table(table_name,previous_table,table_list,field_labels,field_names,data_types,link_tables,parent_tables):
    print("Validating tables for: "+table_name)
    if (table_name == previous_table[0]):   # If table name did not change, don't do anything
        return(True)
    # Table name has changed so clear out values
    previous_table[0] = table_name
    query_name.set("")
    query_desc.set("")
    query_list.clear()
    a3['values']=query_list
    clear_rows(0)
    parent_tables.clear()
    field_labels.clear()
    field_labels.append("")
    field_names.clear()
    field_names.append("")

    # If the table name is blank or invaiid, clear the dropdown values of the fields
    if (table_name == ""):
        for i in range(0,max_rows):
            values[i][1].config(values=field_labels)
        return(True)
    if (table_name not in table_list):
        for i in range(0,max_rows):
            values[i][1].config(values=field_labels)
        return(True)

    get_field_details(table_name,parent_tables,field_labels,field_names,data_types,link_tables)
    for i in range(0,max_rows):
        values[i][1].config(values=field_labels)
    get_queries()
    return(True)

def get_field_details(table_name,parent_tables,field_labels,field_names,data_types,link_tables):
	mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=database_name
        )
	# Get field names and their data types
	parent_tables.append(table_name)       # Add table to list of parent tables
	mycursor = mydb.cursor(buffered=True)
	sql_cmd = "select field_name,field_label,data_type,field_len,link_table,sort_order,parent_table from table_details where (table_name = '"+table_name+"') and (removed='0') order by sort_order"
	mycursor.execute(sql_cmd)
	i = 0
	parent_table = ""
	for x in mycursor:
		if (i == 0):
			parent_table = x[6]
		field_name = table_name+"."+x[0]
		field_label = table_name+"."+x[1]
		field_names.append(field_name)
		field_labels.append(field_label)
		data_types[field_label] = x[2]
		dropdown_values = []
		if (x[4] != "") and (x[4] != None):
		          get_dropdown(x[4],dropdown_values,mydb)
		link_tables[field_label] = dropdown_values
		i += 1
	if (parent_table != "") and (parent_table != None):
		get_field_details(parent_table,parent_tables,field_labels,field_names,data_types,link_tables)

def set_input(event,frame,values,orig_values,data_types,link_tables,col_width):
    widget = event.widget
    row_pos = event.widget.grid_info()["row"]
    print("setting input for row "+str(row_pos))
    field = event.widget.get()
    if (field != orig_values[row_pos]):
        orig_values[row_pos] = field
        if (field == ""):
            values[row_pos][3] = Entry(frame,width=col_width)
        elif (data_types[field] == "VARCHAR"):
            if len(link_tables[field]) == 0:
                values[row_pos][3] = Entry(frame,width=col_width)
            else:
                values[row_pos][3] = ttk.Combobox(frame,width=col_width-2,values=link_tables[field])
        elif (data_types[field] == "INT"):
            values[row_pos][3] = Lotfi(frame,width=col_width)
        elif (data_types[field] == "FLOAT"):
            values[row_pos][3] = Lotfi(frame,width=col_width)
        elif (data_types[field] == "DATE"):
            values[row_pos][3] = DateEntry(frame,width=col_width-2,date_pattern="Y-mm-dd")
        else:
            values[row_pos][3] = Entry(frame,width=col_width)
        values[row_pos][3].grid(row=row_pos,column=3)
    return(True)


def save_query(show_message):
    parent_table = a2.get()
    query_name = a3.get()
    query_desc = a4.get()
    if parent_table == "":
        msg_text = "Error: You must enter a Table Name"
        messagebox.showerror("Error",msg_text)
        return
    if (query_name == ""):
        msg_text = "Error: You must enter a Query Name"
        messagebox.showerror("Error",msg_text)
        return
    save_defaults(parent_table,query_name,query_desc)

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor(buffered=True)
    sql_cmd = "SELECT identifier,query_name,removed,query_description FROM query_header WHERE (query_name = '"+query_name+"') AND (table_name='"+parent_table+"')"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    if mycursor.rowcount <= 0:
        now = datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        sql_cmd = "INSERT INTO query_header (modified_by,modified_on,query_name,query_description,table_name) VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"','"+query_name+"','"+query_desc+"','"+parent_table+"')"
        mycursor.execute(sql_cmd)
        query_header_id = mycursor.lastrowid
        for i in range(max_rows):
            if (values[i][1].get() != ""):
                now = datetime.now()
                cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
                sql_cmd = "INSERT INTO query_details (modified_by,modified_on,query_header,left_paren,field_name,operator,field_value,right_paren,and_or) "
                sql_cmd += "VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"',"+str(query_header_id)+",'"+values[i][0].get()+"','"+values[i][1].get()+"','"+values[i][2].get()+"','"+values[i][3].get()+"','"+values[i][4].get()+"','"+values[i][5].get()+"')"
                mycursor.execute(sql_cmd)
        mydb.commit()
        get_queries() # Update query pulldown to contain newly created query
    else:
        row = mycursor.fetchone()
        query_header_id = row[0]
        removed = row[2]
        sql_cmd = "UPDATE query_header SET query_description = '"+query_desc+"',removed = 0"
        if removed == 1:
            msg_text = "Query is currently removed but will be restored."
            messagebox.showinfo("Information",msg_text)
        sql_cmd += " WHERE identifier = "+str(query_header_id)
        mycursor.execute(sql_cmd)
        sql_cmd = "SELECT identifier FROM query_details WHERE query_header = "+str(query_header_id)+" ORDER BY identifier"
        mycursor.execute(sql_cmd)
        row_count = mycursor.rowcount
        identifiers = []
        for row in mycursor:
            identifiers.append(row[0])
        now = datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        for i in range(max_rows):
            if (values[i][1].get() != "") and (i < row_count):
                sql_cmd = "UPDATE query_details SET modified_by = '"+getpass.getuser()+"',modified_on='"+str(cur_time)+"',"
                sql_cmd += "left_paren='"+values[i][0].get()+"',field_name='"+values[i][1].get()+"',operator='"+values[i][2].get()+"',field_value='"+values[i][3].get()+"',right_paren='"+values[i][4].get()+"',and_or='"+values[i][5].get()+"'"
                sql_cmd += " WHERE (query_header="+str(query_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (values[i][1].get() != "") and (i >= row_count):
                sql_cmd = "INSERT INTO query_details (modified_by,modified_on,query_header,left_paren,field_name,operator,field_value,right_paren,and_or) "
                sql_cmd += "VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"',"+str(query_header_id)+",'"+values[i][0].get()+"','"+values[i][1].get()+"','"+values[i][2].get()+"','"+values[i][3].get()+"','"+values[i][4].get()+"','"+values[i][5].get()+"')"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (values[i][1].get() == "") and (i < row_count):
                sql_cmd = "DELETE FROM query_details WHERE (query_header="+str(query_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
        mydb.commit()
    if show_message:    # If show_message is False, then save_query is called from save_columns which calle generate_sql_command
        generate_sql_command(query_header_id,parent_tables,field_names,field_labels,values,max_rows)
        msg_text = "Query Created/Updated: "+query_name
        messagebox.showinfo("Information",msg_text)
        print("Finished\n")
    return(query_header_id)

def get_tables(*args):
        mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )

        mycursor = mydb.cursor()
        sql_cmd = "SELECT DISTINCT table_name FROM table_details WHERE (table_name NOT LIKE '%_aud') ORDER BY table_name"
        mycursor.execute(sql_cmd)
        table_list.clear()
        for x in mycursor:
            table_list.append(x[0])
        a2['values']=table_list
        if 'max_rows' in globals(): # If called first time, don't clear out parent and child tables
            parent_table.set("")
            query_name.set("")

def get_queries(*args):
    print("Getting queries for "+a2.get())
    if a2.get() == "":
        query_name.set("")
        return
    global table_list
    if (a2.get() not in table_list):
        query_name.set("")
        return
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=database_name
        )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT query_name FROM query_header WHERE (table_name = '"+a2.get()+"') AND (removed = 0) ORDER BY query_name"
    mycursor.execute(sql_cmd)
    query_list.clear()
    for x in mycursor:
        query_list.append(x[0])
    a3['values']=query_list

def myfunction2(event,canvas2):
    canvas2.configure(scrollregion=canvas2.bbox("all"),width=900,height=350)

def get_label(event):
    row_pos = event.widget.grid_info()["row"]
    new_value = event.widget.get()
    #print("row: "+str(row_pos)+" new value: "+new_value)
    if new_value == "":
        return(True)
    field_label = new_value.split(".")[-1]
    column_values[row_pos][1].delete(0,END)
    column_values[row_pos][1].insert(0,field_label)
    return(True)

def get_columns(parent_tables,field_names,field_labels,values,max_rows,data_types,column_values,removed_values):
    new_window = Toplevel(mw)
    new_window.wm_title("Select Columns")
    new_window.geometry('900x500+250+150')

    frame1 = Frame(new_window)
    frame2 = Frame(new_window)
    frame3 = Frame(new_window)
    framebot = Frame(new_window)
    frame1.pack(side=TOP,fill=X)
    frame2.pack(side=TOP,fill=X)
    frame3.pack(side=TOP,fill=X)
    framebot.pack(side=BOTTOM,fill=X)

    w1 = Label(frame1, text="Select Columns ",font=("Times",16)).pack(side="left")

    headers = ["Field Name","Column Label","Sort Order","Remove"]
    col_widths = [30,30,8,6]
    column = 0
    for header in headers:
        l1 = Entry(frame2,relief=FLAT,width=col_widths[column])
        l1.insert(0,header)
        l1.config(state="readonly")
        l1.grid(row=0,column= column)
        column += 1

    canvas2=Canvas(frame3)
    frame=Frame(canvas2)
    myscrollbar=Scrollbar(frame3,orient="vertical",command=canvas2.yview)
    canvas2.configure(yscrollcommand=myscrollbar.set)
    myscrollbar.pack(side="right",fill="y")
    canvas2.pack(side="left")
    canvas2.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",lambda event: myfunction2(event,canvas2))

    column_values.clear()
    column_table(frame,col_widths,column_values,field_labels,removed_values)
    load_saved_columns(column_values,field_labels)

    all_button = Button(framebot,text='Load All',font=("Times",16),command=lambda:load_all(column_values,field_labels)).pack(side="left")
    clear_button = Button(framebot,text='Clear',font=("Times",16),command=lambda:clear_columns(column_values,0)).pack(side="left")
    exit_button = Button(framebot,text='Exit',font=("Times",16),command=new_window.destroy).pack(side="right")
    save_button = Button(framebot,text='Save/Exit',font=("Times",16),command=lambda:save_columns(parent_tables,field_names,field_labels,values,max_rows,data_types,column_values,removed_values,new_window)).pack(side="right")

def load_saved_columns(column_values,field_labels):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier,query_name,removed FROM query_header WHERE (query_name = '"+a3.get()+"') AND (table_name='"+a2.get()+"')"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if (row == None): # New query, no saved columns
        return
    else:
        query_header_id = row[0]

    sql_cmd = "SELECT field_name,field_label,sort_order FROM query_columns WHERE (query_header = "+str(query_header_id)+") ORDER BY sort_order"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    i = 0
    for row in mycursor:
        j = 0
        column_values[i][j].config(state=NORMAL)
        column_label = column_values[i][j].delete(0,END)
        column_label = column_values[i][j].insert(0,row[j])
        column_values[i][j].config(state="readonly")
        j += 1
        column_label = column_values[i][j].delete(0,END)
        column_label = column_values[i][j].insert(0,row[j])
        j += 1
        column_label = column_values[i][j].delete(0,END)
        column_label = column_values[i][j].insert(0,row[j])
        i += 1

def column_table(frame,col_widths,column_values,field_labels,removed_values):
    for i in range(0,max_columns):
      column_values.append([])
      removed_values.append("0")
      removed_values[i] = Variable()
      j = 0
      column_values[i].append(ttk.Combobox(frame,width=col_widths[j],values=field_labels,state="readonly"))
      column_values[i][j].bind("<<ComboboxSelected>>",lambda event:get_label(event))
      column_values[i][j].grid(row=i,  column= j)
      j += 1
      column_values[i].append(Entry(frame,width=col_widths[j]))
      column_values[i][j].grid(row=i,  column= j)
      j += 1
      column_values[i].append(Lotfi(frame,width=col_widths[j]))  # Sort order
      column_values[i][j].grid(row=i,  column= j)
      j += 1
      column_values[i].append(Checkbutton(frame,width=col_widths[j],onvalue="1",offvalue="0",variable=removed_values[i]))  # Sort order
      column_values[i][j].grid(row=i,  column= j)
      removed_values[i].set("0")


def load_all(column_values,field_labels):
    col_index = 0
    for i in range(0,len(field_labels)):
        if (field_labels[i] != ""):
            j = 0
            column_values[col_index][j].config(state=NORMAL)
            column_values[col_index][j].delete(0,END)
            column_values[col_index][j].insert(0,field_labels[i])
            column_values[col_index][j].config(state="readonly")
            j += 1
            temp_var = field_labels[i].split(".",1)[-1]
            column_values[col_index][j].delete(0,END)
            column_values[col_index][j].insert(0,temp_var)
            j += 1
            column_values[col_index][j].delete(0,END)
            column_values[col_index][j].insert(0,str(col_index))
            col_index += 1
    clear_columns(column_values,col_index)

def clear_columns(column_values,start_pos):
    for i in range(start_pos,max_columns):
      j = 0
      column_values[i][j].config(state=NORMAL)
      column_values[i][j].delete(0,END)
      column_values[i][j].config(state="readonly")
      j += 1
      column_values[i][j].delete(0,END)
      j += 1
      column_values[i][j].delete(0,END)
      removed_values[i].set("0")

def save_columns(parent_tables,field_names,field_labels,values,max_rows,data_types,column_values,removed_values,new_window):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier,query_name,removed FROM query_header WHERE (query_name = '"+a3.get()+"') AND (table_name='"+a2.get()+"')"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if (row == None):
        query_header_id = save_query(False)
    else:
        query_header_id = row[0]
    sql_cmd = "SELECT identifier FROM query_columns WHERE query_header = "+str(query_header_id)+" ORDER BY identifier"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    number_of_columns = 0
    identifiers = []
    for row in mycursor:
        identifiers.append(row[0])
        number_of_columns += 1
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    userid = getpass.getuser()
    for i in range(max_columns):
        sort_order = column_values[i][2].get()
        if sort_order == "":
            sort_order = "0"
        if (removed_values[i].get() == "0"):
            if (column_values[i][1].get() != "") and (i < number_of_columns):
                sql_cmd = "UPDATE query_columns SET modified_by = '"+getpass.getuser()+"',modified_on='"+str(cur_time)+"',"
                sql_cmd += "field_name='"+column_values[i][0].get()+"',field_label='"+column_values[i][1].get()+"',sort_order="+sort_order
                sql_cmd += " WHERE (query_header="+str(query_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (column_values[i][1].get() != "") and (i >= number_of_columns):
                sql_cmd = "INSERT INTO query_columns (modified_by,modified_on,query_header,field_name,field_label,sort_order) "
                sql_cmd += "VALUES ('"+userid+"','"+str(cur_time)+"',"+str(query_header_id)+",'"+column_values[i][0].get()+"','"+column_values[i][1].get()+"',"+sort_order+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (column_values[i][1].get() == "") and (i < number_of_columns):
                sql_cmd = "DELETE FROM query_columns WHERE (query_header="+str(query_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
        else:
            if (i < number_of_columns):
                sql_cmd = "DELETE FROM query_columns WHERE (query_header="+str(query_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
    mydb.commit()
    generate_sql_command(query_header_id,parent_tables,field_names,field_labels,values,max_rows)
    new_window.destroy()

def generate_sql_command(query_header_id,parent_tables,field_names,field_labels,values,max_rows):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT field_name,field_label FROM query_columns WHERE (query_header='"+str(query_header_id)+"') ORDER BY sort_order"
    mycursor.execute(sql_cmd)

    sql_query = "SELECT "
    row_count = 0
    for row in mycursor:
        field_index = field_labels.index(row[0])
        sql_query += field_names[field_index]+","
        row_count += 1
    if row_count == 0:
        msg_txt = "No columns entered!"
        messagebox.showerror("Error",msg_txt)
        return
    sql_query = sql_query.rstrip(",")+" FROM "+",".join(parent_tables)+" WHERE "
    for x in parent_tables:
        sql_query += "("+x+".removed = 0) AND "

    for i in range(0,len(parent_tables)-1):
        sql_query += "("+parent_tables[i]+"."+parent_tables[i+1]+" = "+parent_tables[i+1]+".identifier) AND "
    sql_query += "("
    for i in range(0,max_rows):
        field_label = values[i][1].get()
        if (field_label != ""):
            field_index = field_labels.index(field_label)
            field_name = field_names[field_index]
            sql_query += "("*len(values[i][0].get())
            sql_query += field_name
            sql_query += " "+values[i][2].get()
            if (data_types[field_label] == "VARCHAR"):
                sql_query += " '"+values[i][3].get()+"'"
            elif (data_types[field_label] == "DATE"):
                sql_query += " '"+values[i][3].get()+"'"
            else:
                sql_query += " "+values[i][3].get()
            sql_query += ")"*len(values[i][4].get())
            sql_query += " "+values[i][5].get()+" "
    sql_query = sql_query.rstrip(" AND ")   # remove trailing AND or OR
    sql_query = sql_query.rstrip(" OR ")
    sql_query += ")"
    print(sql_query)
    sql_cmd = "UPDATE query_header SET sql_command = \""+sql_query+"\" WHERE (identifier = "+str(query_header_id)+")"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    mydb.commit()

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=900,height=350)

# Start the main program here
if __name__ == "__main__":
    current_file = Path(__file__).stem
    mw=Tk()
    mw.geometry('900x500+200+150')
    mw.title(current_file)

    default_file = expanduser("~")+"/table_maker/"+current_file+".default"
    # If file does not exist, create one
    if not os.path.isfile(default_file):
    		cmd = "touch " + default_file
    		os.system(cmd)
    default_values = open(default_file,"r")

    temp_file = expanduser("~")+"/table_maker/"+current_file+"_temp.csv"

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

    dbase_list = []
    table_list = []     # list of valid tables in database
    parent_tables = []  # list of all parent tables
    query_list = []
    field_labels = []
    field_names = []
    data_types = {}
    link_tables = {}

    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd
        )
    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")
    for x in mycursor:
        dbase_list.append(x[0])

    w2 = Label(frame1, text="Table Name: ",font=("Times",16)).pack(side="left")
    parent_table = StringVar()
    tempvar = default_values.readline()
    parent_table.set(tempvar.strip())
    a2 = ttk.Combobox(frame1,width=40,font=("Times",16),textvar=parent_table,state="readonly")
    a2.bind("<<ComboboxSelected>>",lambda event:validate_table(parent_table.get(),previous_table,table_list,field_labels,field_names,data_types,link_tables,parent_tables))
    a2.pack(side="left")

    w3 = Label(frame2, text="Query Name: ",font=("Times",16)).pack(side="left")
    query_name = StringVar()
    tempvar = default_values.readline()
    query_name.set(tempvar.strip())
    query_name.trace('w',get_records)
    a3 = ttk.Combobox(frame2,width=40,font=("Times",16),textvar=query_name)
    a3.pack(side="left")

    w4 = Label(frame3, text="Query Description: ",font=("Times",16)).pack(side="left")
    query_desc = StringVar()
    tempvar = default_values.readline()
    query_desc.set(tempvar.strip())
    a4 = Entry(frame3,width=40,font=("Times",16),textvar=query_desc)
    a4.pack(side="left")

    headers = ["Left Parens","Field Name","Operator","Value","Right Paren","And/Or"]
    col_widths = [10,30,10,30,10,6]
    column = 0
    for header in headers:
        l1 = Entry(frame4,relief=FLAT,width=col_widths[column])
        l1.insert(0,header)
        l1.config(state="readonly")
        l1.grid(row=0,column= column)
        column += 1

    previous_table = [a2.get()]
    get_tables(database_name)
    get_queries()

    btn1 = Button(framebot,text='Save Query',font=("Times",16),command=lambda:save_query(True)).pack(side="left")
    btn2 = Button(framebot,text='Columns',font=("Times",16),command=lambda: get_columns(parent_tables,field_names,field_labels,values,max_rows,data_types,column_values,removed_values)).pack(side="left")
    btn3 = Button(framebot,text='View Results',font=("Times",16),command=view_results).pack(side="left")
    btn4 = Button(framebot,text='Execute Query',font=("Times",16),command=lambda: execute_query(parent_tables,field_names,field_labels,values,max_rows,data_types,column_values,removed_values)).pack(side="left")
    btn6 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")

    default_values.close()

    field_names.append("")  # Insrt a blank field in case user wants to clear out field
    field_labels.append("")
    if parent_table.get() != "":
        get_field_details(parent_table.get(),parent_tables,field_labels,field_names,data_types,link_tables)

    canvas=Canvas(frame5)
    frame=Frame(canvas)
    myscrollbar=Scrollbar(frame5,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",myfunction)

    values = []
    column_values = []
    removed_values = []
    orig_values = []
    add_column = []
    max_rows = 20
    max_columns = 50
    data_table(frame,col_widths)
    get_records("INIT")

    mw.mainloop()
