from tkinter import *
from tkinter import filedialog
import tkinter.font as font
import os.path
import os
from pathlib import Path
from os.path import expanduser

__author__ = "Kenneth A. Watanabe"
__copyright__ = "Copyright (C) 2020 Kenneth Watanabe"
__license__ = "Public Domain"
__version__ = "4.0"

TABLE_MAKER_DIRECTORY = "/home/table_maker/"
config_file = TABLE_MAKER_DIRECTORY+"table_maker_config.py"


python_modules = []
python_modules.append("tm_settings.py")
python_modules.append("tm_edit_table.py")
python_modules.append("tm_modify_records.py")
python_modules.append("tm_restore_records.py")
python_modules.append("tm_import_data.py")
python_modules.append("tm_export_data.py")
python_modules.append("tm_query.py")
python_modules.append("tm_template.py")
python_modules.append("tm_dashboard.py")

image_files = []
image_files.append("Settings_sized.png")
image_files.append("Modify_table_sized.png")
image_files.append("Modify_record_sized.png")
image_files.append("Restore_record_sized.png")
image_files.append("import_data_sized.png")
image_files.append("export_data_sized.png")
image_files.append("query_icon_sized.png")
image_files.append("templates_sized.png")
image_files.append("Dashboard_sized.png")

tile_names = []
tile_names.append("Settings")
tile_names.append("Create/Edit Table")
tile_names.append("Enter/Modify Records")
tile_names.append("Restore Record Data")
tile_names.append("Import Data")
tile_names.append("Export Data")
tile_names.append("Query Data")
tile_names.append("Templates")
tile_names.append("Dashboard")


def call_module(module_name):
	file1 =  TABLE_MAKER_DIRECTORY+module_name
	cmd = "python3 "+file1
	os.system(cmd)
	if module_name == "tm_settings.py":
		with open(config_file,"r") as f1:
			for line in f1:
				if "database_name=" in line:
					temp_var = line.split("database_name=",1)[1]
					temp_var = temp_var.strip()
					temp_var = temp_var.strip('"')
		dbase_name.set(temp_var)


current_file = __file__

mw = Tk()
# 999x999 is size of window, 999+999 is the location of the window
mw.geometry('1000x600+200+100')
mw.title(current_file)

frame1 = Frame(mw,highlightbackground="black",highlightthickness=1)
frame2 = Frame(mw)
frame2.columnconfigure(0, pad=20)
frame2.columnconfigure(1, pad=20)
frame2.columnconfigure(2, pad=20)
frame2.rowconfigure(0, pad=20)

frame1.pack(side=TOP,fill=X)
frame2.pack()

image_file = TABLE_MAKER_DIRECTORY+"images/Akyo_logo.png"
logo = PhotoImage(file=image_file)

# get database name
try:
	if os.stat(config_file).st_size > 0:
		with open(config_file,"r") as f1:
			for line in f1:
				if "database_name=" in line:
					temp_var = line.split("database_name=",1)[1]
					temp_var = temp_var.strip()
					temp_var = temp_var.strip('"')
except:
	temp_var = ""
dbase_name = StringVar()
dbase_name.set(temp_var)

w1 = Label(frame1, image=logo).grid(row=0,column=0,padx=50,rowspan=2)
w1a = Label(frame1, text="Database Table Maker v4.0",font=("Times",40)).grid(row=0,column=1,padx=25)
w1b = Label(frame1, text="Kenneth A. Watanabe, PhD",font=("Times",20)).grid(row=1,column=1,padx=25)
w1c = Label(frame1, text=temp_var,font=("Times",12),textvariable=dbase_name).grid(row=1,column=2)

image_objects = []
for i in range(0,len(image_files)):
	image_file = TABLE_MAKER_DIRECTORY+"images/"+image_files[i]
	image_objects.append(PhotoImage(file=image_file))

row_pos = 0
col_pos = 0
for i in range(0,len(python_modules)):
	btn = Button(frame2,text=tile_names[i],font=("Times",16),command=lambda python_mod=python_modules[i] :call_module(python_mod),image=image_objects[i],compound=TOP,padx=50)
	btn.config(height=130,width=160)
	btn.grid(row=row_pos,column=col_pos)
	if col_pos >= 2:
		row_pos += 1
		col_pos = 0
	else:
		col_pos += 1

mw.mainloop()
