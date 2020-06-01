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
import datetime
from table_maker_config import hostname,username,ciphered_passwd,database_name
from cryptography.fernet import Fernet
import shutil
import matplotlib
import matplotlib.pyplot as plt
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

def get_queries(query_names):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT query_name FROM query_header ORDER BY query_name"
    mycursor.execute(sql_cmd)
    query_names.clear()
    for row in mycursor:
        query_names.append(row[0])


def data_table(frame4,col_widths,query_names):
    # Create and populate values array
    chart_types = ["Pie","Bar","Line"]
    for i in range(0,max_rows):
               values.append([])
               j = 0
               values[i].append(ttk.Combobox(frame4,width=col_widths[j],values=query_names))
               values[i][j].bind("<<ComboboxSelected>>",lambda event:set_input(event,frame,values,orig_values,30))
               orig_values.append("")
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Entry(frame4,width=col_widths[j]))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Combobox(frame4,width=col_widths[j],values=chart_types))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(ttk.Entry(frame4,width=col_widths[j]))
               values[i][j].grid(row=i,  column= j)

               j += 1
               values[i].append(Lotfi(frame4,width=col_widths[j]))
               values[i][j].grid(row=i,  column= j)

def get_records(*args):
    #if (args[0] == "PY_VAR0"): # if the value of the parent table changed via keystroke
    #    child_table.set("")
    if (a2.get() == ""):
        if 'max_rows' in globals():
            clear_rows(0)
        return

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    if a2.get() in dashboard_ids.keys():
        dashboard_id = dashboard_ids[a2.get()]
    else:
        return
    sql_cmd = "SELECT dashboard_desc FROM dashboard_header WHERE identifier = '"+str(dashboard_id)+"'"
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    a3.delete(0,END)
    a3.insert(0,row[0])

    sql_cmd = "SELECT query_name,category,chart_type,chart_title,sort_order FROM dashboard_details WHERE dashboard_header = '"+str(dashboard_id)+"' ORDER BY sort_order"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    i = 0
    for row in mycursor:
        j = 0
        values[i][j].delete(0,END)
        values[i][j].insert(0,row[j])
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
        i += 1
    clear_rows(i) # Clear our remaining rows


def clear_rows(start_row):
    # Clear out remaining rows
    for i in range(start_row,max_rows):
        j = 0
        values[i][j].delete(0,END)
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].delete(0,END)
        j += 1
        values[i][j].delete(0,END)

def set_input(event,frame,values,orig_values,col_width):
    widget = event.widget
    row_pos = event.widget.grid_info()["row"]
    print("setting input for row "+str(row_pos))
    field = event.widget.get()
    if (field != orig_values[row_pos]):
        orig_values[row_pos] = field
        if (field == ""):
            values[row_pos][1] = Entry(frame,width=col_width)
        else:
            dropdown_values = []
            get_dropdown(field,dropdown_values)
            values[row_pos][1] = ttk.Combobox(frame,width=col_width-2,values=dropdown_values)
        values[row_pos][1].grid(row=row_pos,column=1)
    return(True)

def get_dropdown(query_name,dropdown_values):
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT h.identifier,c.field_name FROM query_columns c,query_header h "
    sql_cmd += "WHERE (h.identifier = c.query_header) and (h.query_name = '"+query_name+"')"
    mycursor.execute(sql_cmd)
    for row in mycursor:
        dropdown_values.append(row[1])

def save_defaults(*args):
    default_values = open(default_file,"w+")
    for x in args:
        default_values.write(x+"\n")
    default_values.close()


def main_program():
    dashboard_name = a2.get()
    dashboard_title = a3.get()
    save_defaults(dashboard_name,dashboard_title)

    if dashboard_name == "":
        return

    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT identifier,dashboard_name,removed,dashboard_desc FROM dashboard_header WHERE dashboard_name ='"+dashboard_name+"'"
    mycursor.execute(sql_cmd)
    row = mycursor.fetchone()
    if row == None:
        now = datetime.datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        sql_cmd = "INSERT INTO dashboard_header (dashboard_name,dashboard_desc,modified_by,modified_on) "
        sql_cmd += "VALUES ('"+dashboard_name+"','"+dashboard_title+"','"+getpass.getuser()+"','"+cur_time+"')"
        print(sql_cmd)
        mycursor.execute(sql_cmd)
        dashboard_header_id = mycursor.lastrowid
        for i in range (max_rows):
            j = 0
            query_name = values[i][j].get()
            j += 1
            category = values[i][j].get()
            j += 1
            chart_type = values[i][j].get()
            j += 1
            chart_title = values[i][j].get()
            j += 1
            sort_order = values[i][j].get()
            if sort_order == "":
                sort_order = "Null"
            if query_name != "":
                sql_cmd = "INSERT INTO dashboard_details (modified_by,modified_on,dashboard_header,query_name,category,chart_type,chart_title,sort_order) "
                sql_cmd += "VALUES ('"+getpass.getuser()+"','"+cur_time+"',"+str(dashboard_header_id)+",'"+query_name+"','"+category+"','"+chart_type+"','"+chart_title+"',"+sort_order+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
        mydb.commit()
    else:
        dashboard_header_id = row[0]
        removed = row[2]
        sql_cmd = "UPDATE dashboard_header SET dashboard_desc = '"+dashboard_title+"',removed = 0"
        if removed == 1:
            msg_text = "Query is currently removed but will be restored."
            messagebox.showinfo("Information",msg_text)
        sql_cmd += " WHERE identifier = "+str(dashboard_header_id)
        mycursor.execute(sql_cmd)
        sql_cmd = "SELECT identifier FROM dashboard_details WHERE dashboard_header = "+str(dashboard_header_id)+" ORDER BY identifier"
        mycursor.execute(sql_cmd)
        #row_count = mycursor.rowcount  # There is a bug in rowcount, it always returns -1
        row_count = 0
        identifiers = []
        for row in mycursor:
            identifiers.append(row[0])
            row_count += 1
        now = datetime.datetime.now()
        cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
        for i in range(max_rows):
            category = values[i][1].get()
            chart_type = values[i][2].get()
            chart_title = values[i][3].get()
            sort_order = values[i][4].get()
            if (sort_order == "") or (sort_order == None):
                sort_order = "Null"
            if (values[i][0].get() != "") and (i < row_count):
                sql_cmd = "UPDATE dashboard_details SET modified_by = '"+getpass.getuser()+"',modified_on='"+str(cur_time)+"',"
                sql_cmd += "query_name='"+values[i][0].get()+"',category='"+category+"',chart_type='"+chart_type+"',chart_title='"+chart_title+"',sort_order="+sort_order
                sql_cmd += " WHERE (dashboard_header="+str(dashboard_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (values[i][0].get() != "") and (i >= row_count):
                sql_cmd = "INSERT INTO dashboard_details (modified_by,modified_on,dashboard_header,query_name,category,chart_type,chart_title,sort_order) "
                sql_cmd += "VALUES ('"+getpass.getuser()+"','"+str(cur_time)+"',"+str(dashboard_header_id)+",'"+values[i][0].get()+"','"+category+"','"+chart_type+"','"+chart_title+"',"+sort_order+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
            elif (values[i][0].get() == "") and (i < row_count):
                sql_cmd = "DELETE FROM dashboard_details WHERE (dashboard_header="+str(dashboard_header_id)+") AND (identifier="+str(identifiers[i])+")"
                print(sql_cmd)
                mycursor.execute(sql_cmd)
        mydb.commit()
    msg_text = "Dashboard Created/Updated: "+dashboard_name
    messagebox.showinfo("Information",msg_text)
    print("Finished\n")

def view_dashboard():
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT d.query_name,d.category,d.chart_type,qh.sql_command,qh.identifier,d.chart_title FROM dashboard_details d,dashboard_header h ,query_header qh "
    sql_cmd += "WHERE (h.dashboard_name = '"+a2.get()+"') AND (h.identifier = d.dashboard_header) AND (d.query_name = qh.query_name) ORDER BY sort_order"
    print(sql_cmd)
    mycursor.execute(sql_cmd)
    query_names = []
    categories = []
    chart_types = []
    sql_commands = []
    chart_titles = []
    num_charts = 0
    for row in mycursor:
        query_names.append(row[0])
        categories.append(row[1])
        chart_types.append(row[2])
        sql_commands.append(row[3])
        chart_titles.append(row[5])
        query_header_id = row[4]
        num_charts += 1

    if (num_charts <= 2):
        grid_max_rows = 1
        grid_max_cols = 2
    elif (num_charts <= 4):
        grid_max_rows = 2
        grid_max_cols = 2
    elif (num_charts <= 6):
        grid_max_rows = 3
        grid_max_cols = 2
    elif (num_charts <= 9):
        grid_max_rows = 3
        grid_max_cols = 3
    elif (num_charts <= 12):
        grid_max_rows = 4
        grid_max_cols = 3
    elif (num_charts <= 16):
        grid_max_rows = 4
        grid_max_cols = 4
    else:
        grid_max_rows = 5
        grid_max_cols = 4

    fig1,axes = plt.subplots(grid_max_rows,grid_max_cols,figsize=(10,6),constrained_layout=True)
    charts = []
    row_pos = 0
    col_pos = 0
    i = 0
    for sql_query in sql_commands:
        # We must find which column is the category
        sql_cmd = "SELECT qc.field_name,qc.query_header "
        sql_cmd += "FROM query_columns qc, query_header qh "
        sql_cmd += "WHERE (qc.query_header = qh.identifier) and (qh.query_name = '"+query_names[i]+"') "
        sql_cmd += "ORDER BY qc.sort_order"
        print(sql_cmd)
        mycursor.execute(sql_cmd)
        rank = 0
        j = 0
        for row in mycursor:
            if row[0] == categories[i]:
                rank = j
            j += 1

        print(sql_query)
        mycursor.execute(sql_query)

        counts = {}
        for row in mycursor:
            categ = row[rank]
            if (categ == None):
                categ = "None"
            if categ in counts.keys():
                counts[categ] += 1
            else:
                counts[categ] = 1

        labels = []
        fracs = []
        for x in counts:
            labels.append(x)
            fracs.append(counts[x])

        # If there is only one row, the axes array has only 1 dimension
        if grid_max_rows == 1:
            if (chart_types[i] == "Pie"):
                # Sort data so that largest and second largest groups are near the top so that labels wont overlap with title
                labels.clear()
                fracs.clear()
                sorted_counts = sorted(counts.items(),key=lambda x:x[1],reverse=True)
                for k in range(1,len(sorted_counts)):
                    labels.append(sorted_counts[k][0])
                    fracs.append(sorted_counts[k][1])
                labels.append(sorted_counts[0][0])
                fracs.append(sorted_counts[0][1])
                axes[i].pie(fracs, labels=labels, autopct='%1.1f%%',radius=1.2,startangle=90)
            elif (chart_types[i] == "Bar"):
                if isinstance(labels[0], datetime.date): # if date, then sort by keys and rotate labels
                    labels.clear()
                    fracs.clear()
                    sorted_counts = sorted(counts.items(),key=lambda x:x[0])
                    for k in range(len(sorted_counts)):
                        labels.append(sorted_counts[k][0])
                        fracs.append(sorted_counts[k][1])
                    axes[i].bar(labels,fracs,align="center")
                    axes[i].tick_params(labelrotation=15)
                else:
                    axes[i].bar(labels,fracs,align="center")
            else: # (chart_types[i] == "Line"):
                if isinstance(labels[0], datetime.date): # if date, then sort by keys and rotate labels
                    labels.clear()
                    fracs.clear()
                    sorted_counts = sorted(counts.items(),key=lambda x:x[0])
                    for k in range(len(sorted_counts)):
                        labels.append(sorted_counts[k][0])
                        fracs.append(sorted_counts[k][1])
                    axes[i].plot(labels,fracs)
                    axes[i].tick_params(labelrotation=15)
                else:
                    axes[i].plot(labels,fracs)
            axes[i].title.set_text(chart_titles[i])
        else:
            if (chart_types[i] == "Pie"):
                # Sort data so that largest and second largest groups are near the top so that labels wont overlap with title
                labels.clear()
                fracs.clear()
                sorted_counts = sorted(counts.items(),key=lambda x:x[1],reverse=True)
                for k in range(1,len(sorted_counts)):
                    labels.append(sorted_counts[k][0])
                    fracs.append(sorted_counts[k][1])
                labels.append(sorted_counts[0][0])
                fracs.append(sorted_counts[0][1])
                axes[row_pos,col_pos].pie(fracs, labels=labels, autopct='%1.1f%%',radius=1.2,startangle=90)
            elif (chart_types[i] == "Bar"):
                if isinstance(labels[0], datetime.date): # if date, then sort by keys and rotate labels
                    labels.clear()
                    fracs.clear()
                    sorted_counts = sorted(counts.items(),key=lambda x:x[0])
                    for k in range(len(sorted_counts)):
                        labels.append(sorted_counts[k][0])
                        fracs.append(sorted_counts[k][1])
                    axes[row_pos,col_pos].bar(labels,fracs,align="center")
                    axes[row_pos,col_pos].tick_params(labelrotation=15)
                else:
                    axes[row_pos,col_pos].bar(labels,fracs,align="center")
                axes[row_pos,col_pos].tick_params(labelsize=7)
            else: # (chart_types[i] == "Line"):
                if isinstance(labels[0], datetime.date): # if date, then sort by keys and rotate labels
                    labels.clear()
                    fracs.clear()
                    sorted_counts = sorted(counts.items(),key=lambda x:x[0])
                    for k in range(len(sorted_counts)):
                        labels.append(sorted_counts[k][0])
                        fracs.append(sorted_counts[k][1])
                    axes[row_pos,col_pos].plot(labels,fracs)
                    axes[row_pos,col_pos].tick_params(labelrotation=15)
                else:
                    axes[row_pos,col_pos].plot(labels,fracs)
                axes[row_pos,col_pos].tick_params(labelsize=7)
            axes[row_pos,col_pos].title.set_text(chart_titles[i])
        col_pos += 1
        if (col_pos >= grid_max_cols):
            row_pos += 1
            col_pos = 0
        i += 1
    # Remove blank charts
    while (col_pos < grid_max_cols) and (col_pos != 0):
        if grid_max_rows == 1:
            fig1.delaxes(axes[col_pos])
        else:
            fig1.delaxes(axes[row_pos][col_pos])
        col_pos += 1
    plt.suptitle(a3.get(),fontsize = 20)
    #plt.tight_layout()  # Prevent charts from overlapping
    plt.show()



def get_dashboards(database_name,dashboard_ids):
    print("database "+database_name)
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        passwd=passwd,
        database=database_name
        )
    mycursor = mydb.cursor()
    sql_cmd = "SELECT dashboard_name,identifier FROM dashboard_header WHERE (removed = 0) ORDER BY dashboard_name"
    mycursor.execute(sql_cmd)
    dashboard_list = []
    for x in mycursor:
        dashboard_list.append(x[0])
        dashboard_ids[x[0]] = x[1]
    a2['values']=dashboard_list

def get_children(event):
    print("database "+database_name)
    mydb = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=passwd,
            database=database_name
            )
    mycursor = mydb.cursor()
    dashboard_name = a2.get()
    mycursor.execute("select distinct table_name from table_details where dashboard_name = '"+dashboard_name+"'")
    child_list = []
    for x in mycursor:
            child_list.append(x[0])
    a3['values']=child_list
    child_table.set("")

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=900,height=350)

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

    mycursor.execute("SHOW DATABASES")
    dbase_list = []
    table_list = []
    for x in mycursor:
        dbase_list.append(x[0])

    w2 = Label(frame2, text="Dashboard Name: ",font=("Times",16)).pack(side="left")
    dashboard_name = StringVar()
    tempvar = default_values.readline()
    dashboard_name.set(tempvar.strip())
    dashboard_name.trace('w',get_records)
    a2 = ttk.Combobox(frame2,width=40,font=("Times",16),textvar=dashboard_name)
    #a2.bind("<<ComboboxSelected>>",get_children)
    a2.pack(side="left")

    w3 = Label(frame3, text="Dashboard Title: ",font=("Times",16)).pack(side="left")
    dashboard_title = StringVar()
    tempvar = default_values.readline()
    dashboard_title.set(tempvar.strip())
    a3 = ttk.Combobox(frame3,width=40,font=("Times",16),textvar=dashboard_title)
    a3.pack(side="left")

    headers = ["Query Name","Category","Chart Type","Chart Title","Sort Order"]
    col_widths = [20,30,10,20,10]
    column = 0
    for header in headers:
        l1 = Entry(frame4,relief=FLAT,width=col_widths[column])
        l1.insert(0,header)
        l1.config(state="readonly")
        l1.grid(row=0,column= column)
        column += 1

    dashboard_ids = {}
    get_dashboards(database_name,dashboard_ids)

    btn1 = Button(framebot,text='Create/Update Dashboard',font=("Times",16),command=main_program).pack(side="left")
    btn2 = Button(framebot,text='View Dashboard',font=("Times",16),command=view_dashboard).pack(side="left")
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
    add_column = []
    removed_values = []
    max_rows = 20
    query_names = []
    get_queries(query_names)
    data_table(frame,col_widths,query_names)
    get_records("INIT")

    mw.mainloop()
