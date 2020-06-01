from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as font
import os
import os.path
from os.path import expanduser
import mysql.connector
import getpass
from datetime import datetime
from tkcalendar import Calendar, DateEntry
import TkTreectrl as treectrl
from table_maker_config import hostname,username,ciphered_passwd,database_name
from cryptography.fernet import Fernet
import importlib
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
        #if self.get().isdigit():
        if isFloat(self.get()):
            # the current value is only digits; allow this
            self.old_value = self.get()
        if self.get() == "":
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)

def isFloat(x):
        try:
            float(x)
            return True
        except:
            return False

def call_pre_entry_action(table_name,field_entries,field_names,template_id):
    if template_id[0] == -1:
        return
    record_values = {}
    i = 0
    for x in field_entries:
        if x.entry_type == "TEXTBOX":
            val = x.get(1.0,END)
        else:
            val = x.get()
        record_values[field_names[i]] = str(val)
        i += 1

    template_module = "template_actions."+database_name+"-"+table_name+"-"+str(template_id[0])
    templ_module = importlib.import_module(template_module,".") # import module
    templ_act = templ_module.template_action() # create object
    templ_act.pre_entry(record_values)

    i = 0
    for x in field_entries:
        if x.read_only == 1:
            x.configure(state="normal")
        if x.entry_type == "TEXTBOX":
            x.delete(1.0,END)
            x.insert(0,record_values[field_names[i]])
        else:
            x.delete(0,END)
            x.insert(0,record_values[field_names[i]])
        if x.read_only == 1:
            x.configure(state="readonly")
        i += 1


def save_defaults(*args):
    default_values = open(default_file,"w+")
    for x in args:
        default_values.write(x+"\n")
    default_values.close()

def get_child_records(field_id_var,child_table,parent_table,find_window,mlb,cfield_names):
    if field_id_var.get() == "":
        return

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd2 = "select identifier,modified_by,modified_on,removed"
    for x in cfield_names:
        sql_cmd2 += ","+x
    sql_cmd2 += " from "+child_table+" where ("+parent_table+" = "+field_id_var.get()+") and (removed=0)"
    mycursor = mydb.cursor()
    print(sql_cmd2)
    mycursor.execute(sql_cmd2)
    identifiers = []
    mlb.listbox.delete(0,'end') # clear out list box
    for row in mycursor:
        identifiers.append(row[0])
        mlb.listbox.insert('end',*map(str,row))

    number_of_fields = len(cfield_names)+5 # We have to add 5 extra column for the identifier, mod by, mod on, removed fields
    sortorder_flags = {}
    for i in range(number_of_fields):
        sortorder_flags[str(i)] = "increasing"

    mlb.listbox.bind('<1>',lambda event: select_child(event,find_window,mlb,identifiers,field_id_var,child_table,parent_table,sql_cmd2))
    mlb.listbox.notify_install('<Header-invoke>')
    mlb.listbox.notify_bind('<Header-invoke>',lambda event: sort_list(event,mlb,sortorder_flags))


def get_record(scroll_frame,table_name,template_id,field_id_var,field_mb_var,field_mo_var,field_names,field_labels,field_entries,label_widgets,orig_mod,child_tables,child_tabs,child_mlbs,child_field_names):
    if field_id_var.get() == "":
        return True

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT template_id from "+table_name+" WHERE identifier = "+field_id_var.get()
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if (row[0] != template_id[0]):
        template_id[0] = row[0]
    load_field_details(scroll_frame,table_name,template_id,mycursor,field_labels,field_names,field_entries,label_widgets)

    sql_cmd = "SELECT identifier,modified_by,modified_on"
    i = 0
    for x in field_names:
        if field_entries[i].entry_type == "FLOAT":
            sql_cmd += ",round("+x+",2)"
        else:
            sql_cmd += ","+x
        i += 1
    sql_cmd += " FROM "+table_name+" WHERE identifier = "+field_id_var.get()
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    field_mb_var.set(row[1])
    field_mo_var.set(row[2])
    orig_mod[0] = row[1]
    orig_mod[1] = str(row[2])
    i = 0
    for x in field_entries:
        if (x.read_only == 1):
            x.configure(state="normal")
        if x.entry_type == "TEXTBOX":
            x.delete(1.0,END)
            if row[i+3] != None:
                x.insert(1.0,row[i+3])
        else:
            x.delete(0,END)
            if row[i+3] != None:
                x.insert(0,row[i+3])
        if (x.read_only == 1):
            x.configure(state="readonly")
        field_entries[i].original_value = row[i+3]
        i += 1

    for i in range(len(child_tables)):
        child_table = child_tables[i]
        child_tab = child_tabs[i]
        child_mlb = child_mlbs[i]
        cfield_names = child_field_names[i]
        get_child_records(field_id_var,child_table,table_name,child_tab,child_mlb,cfield_names)

    return True

# Find all tables associated with selected database and add to table pull-down
def get_tables(database_name,table_list):
    print("database "+ database_name)
    global first_time
    if first_time != 1: # If called the first time, do not clear out table name
        e1.delete(0,END)
    first_time = 0

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "select distinct table_name from table_details order by table_name"
    mycursor.execute(sql_cmd)

    table_list.clear()
    for x in mycursor:
        if (x[0].find("_aud") < 0):
            table_list.append(x[0])
    e1['values']=table_list
    return(True)

def select_cmd(event,find_window,mlb,identifiers,field_id_var):
    info = mlb.listbox.identify(event.x, event.y)
    if len(info) == 0:
        return
    elif info[0] == 'item':
        field_id_var.set(identifiers[info[1]-1])
        print("Selected item:" + str(info[1]-1))
        find_window.destroy()

def select_child(event,find_window,mlb,identifiers,field_id_var,child_table,parent_table,sql_cmd):
    info = mlb.listbox.identify(event.x, event.y)
    if len(info) == 0:     # if user clicks on a blank area
        record_id = 0
        template_id = [-1]
        print("No item selected ")
        modify_records(child_table,template_id,parent_table,record_id,field_id_var.get(),mlb,sql_cmd,identifiers)
    elif info[0] == 'item':    # if user click on an item in the list
        record_id = identifiers[info[1]-1]
        template_id = [-1]
        print("Selected item:" + str(info[1]-1))
        modify_records(child_table,template_id,parent_table,record_id,field_id_var.get(),mlb,sql_cmd,identifiers)


def sort_list(event,mlb,sortorder_flags):
    index = str(event.column)
    mlb.listbox.sort(column=event.column, mode=sortorder_flags[index])
    if sortorder_flags[index] == 'increasing':
        mlb.listbox.column_configure(mlb.listbox.column(event.column), arrow='up')
        sortorder_flags[index] = 'decreasing'
    else:
        mlb.listbox.column_configure(mlb.listbox.column(event.column), arrow='down')
        sortorder_flags[index] = 'increasing'


def select_record(table_name,field_id_var,field_names,field_labels,field_entries,label_widgets):
    find_window = Toplevel(mw)
    find_window.geometry('700x300+400+200')
    find_window.title("Select "+table_name+" Record")
    mlb = treectrl.ScrolledMultiListbox(find_window)
    mlb.pack(side='top', fill='both', expand=1)
    mlb.focus_set()
    mlb.listbox.config(columns=['identifier'] + field_labels,selectmode='extended')
    sql_cmd = "SELECT identifier"
    num_columns = 1
    for x in field_names:
        sql_cmd += ","+x
        num_columns += 1
    sql_cmd += " FROM "+table_name+" WHERE (removed = '0')"

    for i in range(num_columns-1):
        if (field_entries[i].entry_type == "TEXTBOX"):
            field_value = field_entries[i].get(1.0,"end").strip()
            if (field_value != ""):
                sql_cmd += " AND ("+field_names[i]+" LIKE '"+field_value+"%')"
        elif (field_entries[i].get() != "") and (field_entries[i].entry_type == "TEXT"):
            sql_cmd += " AND ("+field_names[i]+" LIKE '"+field_entries[i].get()+"%')"
        elif (field_entries[i].get() != "") and (field_entries[i].entry_type == "DATE"):
            sql_cmd += " AND ("+field_names[i]+" LIKE '"+field_entries[i].get()+"%')"
        elif (field_entries[i].get() != "") and (field_entries[i].entry_type == "INT"):
            sql_cmd += " AND ("+field_names[i]+" = "+field_entries[i].get()+")"
        elif (field_entries[i].get() != "") and (field_entries[i].entry_type == "FLOAT"):
            sql_cmd += " AND ("+field_names[i]+" = "+field_entries[i].get()+")"
        elif (field_entries[i].get() != ""):
            sql_cmd += " AND ("+field_names[i]+" = '"+field_entries[i].get()+"')"

    identifiers = []
    load_list_box(mlb,sql_cmd,identifiers,num_columns)

    sortorder_flags = {}
    for i in range(num_columns):
        sortorder_flags[str(i)] = "increasing"

    mlb.listbox.bind('<1>',lambda event: select_cmd(event,find_window,mlb,identifiers,field_id_var))
    mlb.listbox.notify_install('<Header-invoke>')
    mlb.listbox.notify_bind('<Header-invoke>', lambda event: sort_list(event,mlb,sortorder_flags))

def load_list_box(mlb,sql_cmd,identifiers,num_columns):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    print("SQL cmd: "+sql_cmd)
    mycursor.execute(sql_cmd)
    for row in mycursor:
        identifiers.append(row[0])
        temp_row = []
        temp_row.append(str(row[0]).rjust(10))    # right justify identifier so that it sorts properly
        for i in range(1,num_columns):
            temp_row.append(str(row[i]))
        mlb.listbox.insert('end',*temp_row)

def reload_multi_list_box(mlb,new_window,sql_cmd,identifiers):
    print("Reloading List Box ")
    mlb.listbox.delete(0,'end')
    mydb = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=passwd,
                database=database_name
                )
    mycursor = mydb.cursor()
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    mlb.listbox.delete(0,'end')
    identifiers.clear()
    for row in mycursor:
        identifiers.append(row[0])
        mlb.listbox.insert('end',*map(str,row))
    new_window.destroy()

def get_dropdown(source,record_list):
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=database_name
        )
    mycursor = mydb.cursor()

    dot_pos = source.find(".")
    table_name = source[0:dot_pos]
    if (table_name not in table_list):
        return
    field_name = source[dot_pos+1:len(source)]
    sql_cmd = "select "+field_name+" from "+table_name+" where removed = 0"
    mycursor.execute(sql_cmd)
    for x in mycursor:
           record_list.append(x[0])

def load_field_details(scroll_frame,table_name,template_id,mycursor,field_labels,field_names,field_entries,label_widgets):
    sql_cmd = "SELECT field_name,field_label,data_type,field_len,link_table,sort_order,parent_table,'',0,1,0 FROM table_details WHERE (table_name = '"+table_name+"') AND (removed='0') ORDER BY sort_order"
    if template_id[0] != None:
        if template_id[0] >= 0:
            sql_cmd = "SELECT tbl.field_name,tmp.field_label,tbl.data_type,tbl.field_len,tbl.link_table,tmp.sort_order,tbl.parent_table,tmp.def_value,tmp.disp,tmp.copy,tmp.mand "
            sql_cmd += "FROM table_details tbl,template_details tmp "
            sql_cmd += "WHERE (tbl.field_name = tmp.field_name) AND (tbl.table_name = '"+table_name+"') and (template_header = "+str(template_id[0])+") and (tmp.removed = 0) ORDER BY tmp.sort_order"
    print(sql_cmd)
    mycursor.execute(sql_cmd)

    for x,y in zip(field_entries,label_widgets):
        x.destroy()
        y.destroy()

    field_names.clear()
    field_labels.clear()
    field_entries.clear()
    label_widgets.clear()

    i = 0
    for x in mycursor:
        # If table is a child table, add a prompt for the parent record
        if i == 0:
            if (x[6] != None) and (x[6] != ""):
                field_names.append(x[6])
                field_labels.append(x[6])
                label_widgets.append(Label(scroll_frame, text=x[6],font=("Times",16)))
                label_widgets[i].grid(row=i,column=0)
                field_entries.append(Lotfi(scroll_frame,width=11,font=("Times",16),state="readonly"))
                field_entries[i].original_value = ""
                field_entries[i].entry_type = "INT"
                field_entries[i].grid(sticky="w",row=i,column=1)
                field_entries[i].default_value = ""
                field_entries[i].read_only = 1
                field_entries[i].copy_value = 1
                field_entries[i].mandatory = 1

                i += 1

        field_names.append(x[0])
        field_labels.append(x[1])

        text_val = x[1]
        if (x[10] == 1):
            text_val = x[1]+">" # Put a ">" after mandatory fields
        label_widgets.append(Label(scroll_frame, text=text_val,font=("Times",16)))
        label_widgets[i].grid(row=i,column=0)
        if (x[4] != "") and (x[4] != None): # Link table
            record_list=[]
            if (x[8] == 0):
                get_dropdown(x[4],record_list)
                field_entries.append(ttk.Combobox(scroll_frame,width=x[3]+1,font=("Times",16),values=record_list))
            else:
                field_entries.append(Entry(scroll_frame,width=x[3],font=("Times",16)))
            field_entries[i].insert(0,x[7])
            field_entries[i].entry_type = "TEXT"
        elif (x[2] == "DATE"):
            field_entries.append(DateEntry(scroll_frame,width=20,font=("Times",16),date_pattern="Y-mm-dd"))
            field_entries[i].configure(validate="none")
            field_entries[i].delete(0,END)
            if x[7] != "":
                field_entries[i].insert(0,x[7])
            field_entries[i].entry_type = "DATE"
        elif (x[2] == "INT") or (x[2] == "FLOAT"):
            field_entries.append(Lotfi(scroll_frame,width=11,font=("Times",16)))
            field_entries[i].insert(0,x[7])
            field_entries[i].entry_type = x[2]
        else:
            if x[3] < 65:
                field_entries.append(Entry(scroll_frame,width=x[3],font=("Times",16)))
                field_entries[i].insert(0,x[7])
                field_entries[i].entry_type = "TEXT"
            else:
                height = int(x[3]/65)+1
                field_entries.append(Text(scroll_frame,width=65,height=height,font=("Times",16)))
                field_entries[i].insert(1.0,x[7])
                field_entries[i].entry_type = "TEXTBOX"
        if (x[8] == 1):
            field_entries[i].configure(state="readonly")
        field_entries[i].default_value = x[7]
        field_entries[i].original_value = x[7]
        field_entries[i].read_only = x[8]
        field_entries[i].copy_value = x[9]
        field_entries[i].mandatory = x[10]
        field_entries[i].grid(sticky="w",row=i,column=1)
        i+=1

# Set scrollable region
def myfunction(event,canvas):
    canvas.configure(scrollregion=canvas.bbox("all"),width=898,height=350)


def main_program():
    table_name = e1.get()
    template_name = e2.get()
    parent_table = ""
    save_defaults(table_name,template_name)
    record_id = 0
    parent_record = 0
    mlb = treectrl.ScrolledMultiListbox(mw)    # Create null mlb and sql_cmd for first call to modify_records
    sql_cmd = "SELECT NULL LIMIT 0"
    identifiers = []
    if template_name == "":
        template_id = [-1]
    else:
        template_id = [template_ids[template_name]]
    modify_records(table_name,template_id,parent_table,record_id,parent_record,mlb,sql_cmd,identifiers)

def modify_records(table_name,template_id,parent_table,record_id,parent_record,mlb,parent_sql_cmd,identifiers):
    new_window = Toplevel(mw)
    new_window.wm_title("Modify "+table_name+" Record")
    new_window.geometry('920x550+250+150')
    new_window.protocol("WM_DELETE_WINDOW",lambda: reload_multi_list_box(mlb,new_window,parent_sql_cmd,identifiers))

    TAB_CONTROL = ttk.Notebook(new_window)
    #Tab1
    TAB1 = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(TAB1, text=table_name)
    TAB_CONTROL.pack(expand=1, fill="both")

    new_frame1 = Frame(TAB1)
    new_frame2 = Frame(TAB1,highlightthickness=1,highlightcolor="gray",highlightbackground="gray")
    new_frame3 = Frame(TAB1)
    new_frame1.pack(side=TOP,fill=X)
    new_frame2.pack(side=TOP,fill=X)
    new_frame3.pack(side=BOTTOM,fill=X)

    label1 = Label(new_frame1, text="Identifier",font=("Times",16))
    label1.grid(row=0,column=0)
    field_id_var = StringVar()
    field_id = Entry(new_frame1,width=40,font=("Times",16),textvariable = field_id_var,validate="focusout",validatecommand=lambda: get_record(scroll_frame,table_name,template_id,field_id_var,field_mb_var,field_mo_var,field_names,field_labels,field_entries,label_widgets,orig_mod,child_tables,child_tabs,child_mlbs,child_field_names))
    field_id.grid(row=0,column=1)

    find_button = Button(new_frame1,text='Find',font=("Times",16),command=lambda: select_record(table_name,field_id_var,field_names,field_labels,field_entries,label_widgets))
    find_button.grid(row=0,column=2)


    label1 = Label(new_frame1, text="Modified By",font=("Times",16))
    label1.grid(row=1,column=0)
    field_mb_var = StringVar()
    field_mb = Entry(new_frame1,width=40,font=("Times",16),state="readonly",textvariable=field_mb_var)
    field_mb.grid(row=1,column=1)

    label1 = Label(new_frame1, text="Modified On",font=("Times",16))
    label1.grid(row=2,column=0)
    field_mo_var = StringVar()
    field_mo = Entry(new_frame1,width=40,font=("Times",16),state="readonly",textvariable=field_mo_var)
    field_mo.grid(row=2,column=1)

    # The following code will create a canvas and scrollbar for the fields in new_frame2
    canvas=Canvas(new_frame2)
    scroll_frame=Frame(canvas)
    myscrollbar=Scrollbar(new_frame2,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=scroll_frame,anchor='nw')
    scroll_frame.bind("<Configure>",lambda event: myfunction(event,canvas))

    # Get table fields
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor(buffered=True)

    # check if there are child tables
    sql_cmd = "SELECT table_name FROM table_header WHERE (parent_table = '"+table_name+"') ORDER BY identifier"
    mycursor.execute(sql_cmd)
    child_tables = []
    child_field_names = []
    child_tabs = []
    child_mlbs = []
    i = 0
    for row in mycursor: # Check if the list is not empty
        child_tables.append(row[0])
        child_tabs.append(ttk.Frame(TAB_CONTROL))
        TAB_CONTROL.add(child_tabs[i], text=row[0])
        child_field_names.append([])

        mycursor2 = mydb.cursor()
        sql_cmd = "select field_name,field_label,data_type,field_len,link_table,sort_order,parent_table from table_details where (table_name = '"+row[0]+"') and (removed='0') order by sort_order"
        mycursor2.execute(sql_cmd)

        child_field_labels = []
        for x in mycursor2:
            child_field_names[i].append(x[0])
            child_field_labels.append(x[1])

        child_mlbs.append(treectrl.ScrolledMultiListbox(child_tabs[i]))
        child_mlbs[i].pack(side='top', fill='both', expand=1)
        child_mlbs[i].listbox.config(columns=['Identifier','Modified by','Modified on','Removed'] + child_field_labels,selectmode='extended')
        i += 1

    field_labels = []
    field_names = []
    field_entries = []
    label_widgets = []
    load_field_details(scroll_frame,table_name,template_id,mycursor,field_labels,field_names,field_entries,label_widgets)
    call_pre_entry_action(table_name,field_entries,field_names,template_id)

    orig_mod = ["",""]

    create_button = Button(new_frame3,text='Create Record',font=("Times",16),command=lambda: create_record(table_name,template_id,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod)).pack(side="left")
    update_button = Button(new_frame3,text='Update Record',font=("Times",16),command=lambda: update_record(table_name,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod)).pack(side="left")
    remove_button = Button(new_frame3,text='Remove Record',font=("Times",16),command=lambda: remove_record(table_name,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod)).pack(side="left")
    audit_button = Button(new_frame3,text='Audit History',font=("Times",16),command=lambda: audit_record(table_name,field_id_var,field_names,field_labels)).pack(side="left")
    clear_button = Button(new_frame3,text='Clear',font=("Times",16),command=lambda: clear_record(table_name,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets)).pack(side="left")
    template_button = Button(new_frame3,text='Template',font=("Times",16),command=lambda: prompt_for_template(scroll_frame,table_name,field_labels,field_names,field_entries,label_widgets,template_id,field_id_var,field_mb_var,field_mo_var,parent_record)).pack(side="left")
    exit_button = Button(new_frame3,text='Exit',font=("Times",16),command=lambda: reload_multi_list_box(mlb,new_window,parent_sql_cmd,identifiers)).pack(side="right")

    if record_id > 0:
        field_id_var.set(record_id)
    if int(parent_record) > 0:  # If child table, set parent table field
        field_entries[0].configure(state="normal")
        field_entries[0].delete(0,END)
        field_entries[0].insert(0,parent_record)
        field_entries[0].configure(state="readonly")

def prompt_for_template(scroll_frame,table_name,field_labels,field_names,field_entries,label_widgets,template_id,field_id_var,field_mb_var,field_mo_var,parent_record):

    new_window = Toplevel(mw)
    new_window.wm_title("Select Tempate for Create Records")
    new_window.geometry('600x200+350+250')

    frame1 = Frame(new_window)
    frame1.pack(side=TOP,fill=X)
    frame_bot = Frame(new_window)
    frame_bot.pack(side=BOTTOM,fill=X)

    label1 = Label(frame1,text="Template ID:",font=("Times",16)).pack(side=LEFT)
    temp_entry = ttk.Combobox(frame1,width=40,font=("Times",16))
    temp_entry.pack(side=LEFT)

    template_list = []
    template_ids = {}
    get_templates(table_name,template_list,template_ids,temp_entry)

    btn1 = Button(frame_bot,text='Continue',font=("Times",16),command=lambda: reset_fields(new_window,scroll_frame,table_name,temp_entry,field_labels,field_names,field_entries,label_widgets,template_id,field_id_var,field_mb_var,field_mo_var,parent_record)).pack(side=LEFT)
    btn2 = Button(frame_bot,text='Exit',font=("Times",16),command=new_window.destroy).pack(side=RIGHT)

def reset_fields(new_window,scroll_frame,table_name,temp_entry,field_labels,field_names,field_entries,label_widgets,template_id,field_id_var,field_mb_var,field_mo_var,parent_record):
    field_id_var.set("")
    field_mb_var.set("")
    field_mo_var.set("")

    temp_name = temp_entry.get()
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    if temp_name == "":
        template_id[0] = -1
    else:
        sql_cmd = "SELECT identifier FROM template_header WHERE (table_name = '"+table_name+"') AND (name='"+temp_name+"')"
        mycursor.execute(sql_cmd)
        row = mycursor.fetchone()
        template_id[0] = row[0]
    load_field_details(scroll_frame,table_name,template_id,mycursor,field_labels,field_names,field_entries,label_widgets)
    if int(parent_record) > 0:
        field_entries[0].configure(state="normal")
        field_entries[0].delete(0,END)
        field_entries[0].insert(0,parent_record)
        field_entries[0].configure(state="readonly")
    call_pre_entry_action(table_name,field_entries,field_names,template_id)
    new_window.destroy()

def display_message(msg_text,table_name,template_id,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod):
    new_window = Toplevel(mw)
    new_window.wm_title("Information")
    new_window.geometry('400x100+500+300')

    frame1 = Frame(new_window)
    frame1.pack(side=TOP,fill=X)
    frame_bot = Frame(new_window)
    frame_bot.pack(side=BOTTOM,fill=X)

    image1 = PhotoImage(file=r'/home/table_maker/images/lightbulb.png')
    label0 = Label(frame1, image=image1)
    label0.image=image1
    label0.grid(row=0,column=0)
    label1 = Label(frame1,text=msg_text,font=("Times",16,"bold")).grid(row=0,column=1)


    btn1 = Button(frame_bot,text='Done',font=("Times",16),command=new_window.destroy).pack(side=LEFT)
    btn2 = Button(frame_bot,text='Create Another',font=("Times",16),command=lambda:close_window(new_window,table_name,template_id,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,orig_mod)).pack(side=RIGHT)

def close_window(new_window,table_name,template_id,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,orig_mod):
    field_id_var.set("")
    field_mb_var.set("")
    field_mo_var.set("")

    # reset default values
    i = 0
    for x in field_entries:
        if (field_names[i] != parent_table):
            if x.copy_value == 0: # reset value if copy flag not set
                if x.read_only == 1:
                    x.configure(state="normal")
                if x.entry_type == "TEXTBOX":
                    x.delete(1.0,END)
                    x.insert(1.0,dev_values[i])
                else:
                    x.delete(0,END)
                    x.insert(0,field_entries[i].default_value)
                if x.read_only == 1:
                    x.configure(state="readonly")
        i += 1
    call_pre_entry_action(table_name,field_entries,field_names,template_id)
    new_window.destroy()

def create_record(table_name,template_id,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod):

    record_values = {}
    i = 0
    for x in field_entries:
        if x.entry_type == "TEXTBOX":
            val = x.get(1.0,END)
        else:
            val = x.get()
        if (x.mandatory == 1) and (val == ""):
            msg_text = "Error: Mandatory fields must have a value."
            messagebox.showerror("Error",msg_text,parent=new_window)
            return
        record_values[field_names[i]] = str(val)
        i += 1

    if (template_id[0] != -1):
        template_module = "template_actions."+database_name+"-"+table_name+"-"+str(template_id[0])
        templ_module = importlib.import_module(template_module,".") # import module
        templ_act = templ_module.template_action() # create object
        templ_act.post_entry(record_values)


    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "INSERT INTO "+table_name+" (modified_by,modified_on,template_id,"
    sql_cmd += ",".join(record_values.keys())
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_cmd += ") VALUES ('"+getpass.getuser()+"','"+cur_time+"',"+str(template_id[0])
    for x in record_values.values():
        if x == '':
            sql_cmd += ",Null"
        else:
            sql_cmd += ",'"+str(x)+"'"
    sql_cmd += ")"

    print(sql_cmd)
    mycursor.execute(sql_cmd)
    mydb.commit()
    field_id_var.set(str(mycursor.lastrowid))
    field_mb_var.set(getpass.getuser())
    field_mo_var.set(cur_time)

    record_values["identifier"] = field_id_var
    if (template_id[0] != -1):
        template_module = "template_actions."+database_name+"-"+table_name+"-"+str(template_id[0])
        templ_module = importlib.import_module(template_module,".") # import module
        templ_act = templ_module.template_action() # create object
        templ_act.post_create(record_values)

    msg_text = "Record Created "+str(field_id_var.get())
    display_message(msg_text,table_name,template_id,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod)


def update_record(table_name,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_cmd = "UPDATE "+table_name+" SET modified_by = '"+getpass.getuser()+"',modified_on = '"+str(cur_time)+"'"
    sql_cmd2 = "INSERT INTO "+table_name+"_aud (identifier,modified_by,modified_on"
    i = 0
    for x,y in zip(field_names,field_entries):
        if y.entry_type == "TEXTBOX":
            temp_var = y.get(1.0,END)
        else:
            temp_var = y.get()
        if temp_var != "":
            sql_cmd += ","+x+"='"+temp_var+"'"
            sql_cmd2 += ","+x
        else:
            sql_cmd += ","+x+"=NULL"
            sql_cmd2 += ","+x
        i += 1
    sql_cmd += " where identifier = "+field_id_var.get()
    print(sql_cmd)
    mycursor.execute(sql_cmd)

    sql_cmd2 += ") VALUES ("+field_id_var.get()+",'"+orig_mod[0]+"','"+orig_mod[1]+"'"
    number_of_fields = len(field_names)
    for x in range(number_of_fields):
        if (field_entries[x].original_value == None) or (field_entries[x].original_value == ""):
            sql_cmd2 += ",NULL"
        else:
            sql_cmd2 += ",'"+str(field_entries[x].original_value)+"'"
    sql_cmd2 += ")"
    print(sql_cmd2)
    mycursor.execute(sql_cmd2)

    # reset original values to new record in case record is updated again
    orig_mod[0] = getpass.getuser()
    orig_mod[1] = str(cur_time)
    i = 0
    for y in field_entries:
        if y.entry_type == "TEXTBOX":
            y.original_value = y.get(1.0,END)
        else:
            y.original_value = y.get()
        i += 1

    mydb.commit()

    field_mb_var.set(getpass.getuser())
    field_mo_var.set(cur_time)
    msg_text = "Record Updated "+str(field_id_var.get())
    messagebox.showinfo("Information",msg_text,parent=new_window)

def remove_record(table_name,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets,new_window,orig_mod):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    now = datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_cmd = "UPDATE "+table_name+" SET modified_by = '"+getpass.getuser()+"',modified_on = '"+str(cur_time)+"',"
    sql_cmd += "removed = '1' where identifier = "+field_id_var.get()
    print(sql_cmd)
    mycursor.execute(sql_cmd)

    sql_cmd2 = "INSERT INTO "+table_name+"_aud (identifier,modified_by,modified_on,removed"
    i = 0
    for x,y in zip(field_names,field_entries):
        sql_cmd2 += ","+x
        i += 1
    sql_cmd2 += ") VALUES ("+field_id_var.get()+",'"+orig_mod[0]+"','"+orig_mod[1]+"','0'"
    number_of_fields = len(field_names)
    for x in range(number_of_fields):
        if field_entries[x].original_value == None:
            sql_cmd2 += ",NULL"
        else:
            sql_cmd2 += ",'"+str(field_entries[x].original_value)+"'"
    sql_cmd2 += ")"
    print(sql_cmd2)
    mycursor.execute(sql_cmd2)
    mydb.commit()

    msg_text = "Record Removed "+str(field_id_var.get())
    messagebox.showinfo("Information",msg_text,parent=new_window)

    # clear our fields
    field_id_var.set("")
    field_mb_var.set("")
    field_mo_var.set("")
    for x in field_entries:
        if x.entry_type == "TEXTBOX":
            x.delete(1.0,END)
        else:
            x.delete(0,END)

def audit_record(table_name,field_id_var,field_names,field_labels):
    if field_id_var.get() == "":
        return
    find_window = Toplevel(mw)
    find_window.geometry('700x300+400+200')
    find_window.title('Select Record')
    mlb = treectrl.ScrolledMultiListbox(find_window)
    mlb.pack(side='top', fill='both', expand=1)
    mlb.focus_set()
    mlb.listbox.config(columns=['Identifier','Modified by','Modified on','Removed'] + field_labels,selectmode='extended')
    sql_cmd = "select identifier,modified_by,modified_on,removed"
    for x in field_names:
        sql_cmd += ","+x
    sql_cmd += " from "+table_name+"_aud where identifier = "+field_id_var.get()
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    for row in mycursor:
        mlb.listbox.insert('end',*map(str,row))

    number_of_fields = len(field_names)+4  # We have to add 4 extra column for the identifier, mod bu, mod on, removed fields
    sortorder_flags = {}
    for i in range(number_of_fields):
        sortorder_flags[str(i)] = "increasing"

    mlb.listbox.notify_install('<Header-invoke>')
    mlb.listbox.notify_bind('<Header-invoke>', lambda event: sort_list(event,mlb,sort_order_flags))

def clear_record(table_name,parent_table,field_id_var,field_mb_var,field_mo_var,field_names,field_entries,label_widgets):
    print("Clear Record")
    field_id_var.set("")
    field_mb_var.set("")
    field_mo_var.set("")
    i = 0
    for x in field_entries:
        if (field_names[i] != parent_table):
            field_entries[i].configure(state="normal")  # must change state to normal to clear
            if x.entry_type == "TEXTBOX":
                x.delete(1.0,END)
            else:
                x.delete(0,END)
        i += 1

def get_templates(table_name,template_list,template_ids,entry_widget):
    print("database "+database_name)
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name,identifier FROM template_header where table_name = '"+table_name+"'")
    template_list.clear()
    template_list.append("")
    template_ids.clear()
    template_ids[""] = 0
    for x in mycursor:
        template_list.append(x[0])
        template_ids[x[0]] = x[1]
    entry_widget.configure(values=template_list)

current_file = Path(__file__).stem
mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('600x200+400+200')
mw.title(current_file)

# Set font of tabs
s = ttk.Style()
s.configure('TNotebook.Tab', font=('Times','16','bold') )

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

w1 = Label(frame1, text="Table Name: ",font=("Times",16)).pack(side="left")
table_name = StringVar()
tempvar = default_values.readline()
table_name.set(tempvar.strip())
e1 = ttk.Combobox(frame1,width=40,font=("Times",16),state="readonly",textvar=table_name,validate="focusout",validatecommand=lambda: get_templates(e1.get(),template_list,template_ids,e2))
e1.pack(side="left")

w2 = Label(frame2, text="Template Name: ",font=("Times",16)).pack(side="left")
template_name = StringVar()
tempvar = default_values.readline()
template_name.set(tempvar.strip())
e2 = ttk.Combobox(frame2,width=40,font=("Times",16),state="readonly",textvar=template_name)
e2.pack(side="left")

btn3 = Button(framebot,text='Go',font=("Times",16),command=main_program).pack(side="left")
btn4 = Button(framebot,text='Exit',font=("Times",16),command=mw.quit).pack(side="right")

default_values.close()

first_time = 1
table_list = []
template_list = []
template_ids = {}
get_tables(database_name,table_list)
if e1.get() != "":
    get_templates(e1.get(),template_list,template_ids,e2)

mw.mainloop()
