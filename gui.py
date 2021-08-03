import os
import subprocess
import shutil
from sys import stderr, stdout
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from subprocess import call, run
import docker
from docker.api import volume
import config

pdk_root = ""
openlane_root = ""
project_path = ""

def start():
    project_name_entry.grid_forget()
    create_project_btn.grid_forget()
    label.configure(text="Creating your project please wait..")
    root.after(1, create_design)

def replace_content(text, query, file):
    reading_file = open(file, "r")
    new_file_content = ""

    for line in reading_file:
        stripped_line = line.strip()
        line_one = stripped_line.replace(query, text)
        new_file_content += line_one + "\n"

    reading_file.close()

    writing_file = open(file, "w")   
    writing_file.write(new_file_content)
    writing_file.close()

def read_env_variables():
    try:
        global pdk_root
        global openlane_root
        pdk_root = os.environ["PDK_ROOT"]
        openlane_root = os.environ["OPENLANE_ROOT"]
        print(pdk_root)
        print(openlane_root)
        return True
    except:
        print("Cannot read PDK_ROOT or OPENLANE_ROOT variables, make sure they are set first")
        return False

def open_existing_project():
    print("opening existing project...")
    if read_env_variables() == True:
        label.configure(text="Select your project")
        open_existing_btn.grid_forget()
        open_new_btn.grid_forget()
        browse_dir_btn.grid(row=2, column=0, columnspan=3, pady=10)
    else:
        pass
    


def create_design():
    print("entry is " + project_name.get())
    print(openlane_root)
    
    client = docker.from_env()
    container = client.containers.run('efabless/openlane:current', command='./flow.tcl -design ' + project_name.get() + ' -init_design_config', 
        volumes={openlane_root: {'bind': '/openLANE_flow', 'mode': 'rw'},
                 pdk_root: {'bind': pdk_root, 'mode':'rw'}},
        environment=["PDK_ROOT=" + pdk_root],
        user=1001,
        detach=True,
        stdout=True,
        stderr=True)
    label.configure(text="Done creating your project. Check the output below if it is a success or error")
    prep_design_console.insert('1.0', container.logs().decode('utf-8'))
    prep_design_console.grid(row=2, column=0)
    proceed_btn.grid(row=3, column=0, columnspan=3, pady=10)

def create_new_project():
    print("creating new project...")
    if read_env_variables() == True:
        label.configure(text="Set a name for the project")
        open_existing_btn.grid_forget()
        open_new_btn.grid_forget()
        project_name_entry.grid(row=2, column=0)
        create_project_btn.grid(row=2, column=1)
    else:
        pass

def proceed():
    prep_design_console.grid_forget()
    proceed_btn.grid_forget()
    label.configure(text="Upload your verilog files")
    browse_file_btn.grid(row=2, columnspan=3, pady=10)

def browse_files():
    global filepath; filepath = filedialog.askopenfilename(initialdir="/home/",
                                          title="Select a File",
                                          filetypes= (("Verilog files", "*.v*"),))
    label.configure(text="File selected: " + filepath)
    global filename
    filename = os.path.basename(filepath)
    browse_file_btn.grid_forget()
    upload_verilog_btn.grid(row=2, columnspan=3, pady=10)

def browse_dir():
    global project_path
    project_path = filedialog.askdirectory(initialdir=openlane_root, title="Select your project")
    print(project_path)
    project_name = os.path.basename(project_path)
    projects = os.listdir(openlane_root+"/designs")
    if project_name not in projects:
        label.configure(text="your project does not exist or the path you selected is not appropriate. Please browse again..")
    else:
        label.configure(text="project is found successfully")
        browse_dir_btn.grid_forget()
        next_btn.grid(row=2, columnspan=3, pady=10)


def upload_selected_verilog():
    try:
        shutil.copy(filepath, openlane_root+"/designs/"+project_name.get()+"/src/"+filename)
        label.configure(text="file is added to your design's src/ folder")
        upload_verilog_btn.grid_forget()
        next_btn.grid(row=2, columnspan=3, pady=10)
    except shutil.SameFileError:
        label.configure(text="source and destination represents the same file")
    except PermissionError:
        label.configure(text="Permission denied")
    except:
        label.configure(text="Error occured while copying the file to the design's folder")

def clk_metric_changed():
    print("clock check value: " + str(clock_en.get()))
    if(clock_en.get() == 1):
        clk_period_label.grid(row=4, column=0)
        clk_period_entry.grid(row=4, column=1)
        clk_port_label.grid(row=5, column=0)
        clk_port_entry.grid(row=5, column=1)
    else:
        clk_period_label.grid_forget()
        clk_period_entry.grid_forget()
        clk_port_label.grid_forget()
        clk_port_entry.grid_forget()


def begin_param_insertion():
    label.configure(text="Set the design parameters as you like. Fields left empty will have defualt values.")
    next_btn.grid_forget()
    top_name_label.grid(row=2, column=0)
    top_name_entry.grid(row=2, column=1)
    clock_en_check.grid(row=3, column=0)
    begin_run_btn.grid(row=6, column=0)

def begin_openlane_run():
    print("clock enable is: " + str(clock_en.get()))
    f = open(project_path+"/config.tcl", 'w')
    if(top_name.get() != ""):
        config.set_design_name(name=top_name.get(), file=f)
    else:
        print("ERROR: please provide a top name of the design")
    f.write('set ::env(VERILOG_FILES) [glob $::env(DESIGN_DIR)/src/*.v]\n')
    if(clock_en.get() == 0):
        # user does not have clock in their design
        config.set_no_clock(file=f)
    elif(clock_en.get() == 1 and clk_period.get() != "" and clk_port.get() != ""):
        # user has clock in their design and has given values for it
        config.set_clock_definition(clk_port=clk_port.get(), clk_period=clk_period.get(), file=f)
    else:
        print("ERROR: some required fields are missing for clock")

    f.write('set filename $::env(DESIGN_DIR)/$::env(PDK)_$::env(STD_CELL_LIBRARY)_config.tcl \n')
    f.write('if { [file exists $filename] == 1} { \n')
    f.write('source $filename \n')
    f.write('} \n')
    f.close()


root = Tk()
root.title("OpenLANE Graphical User Interface")
frame = ttk.Frame(root) 
label = ttk.Label(frame, text="Do you like to create a new project or open an existing one?")
open_existing_btn = ttk.Button(frame, text="Open existing project", command=open_existing_project)
open_new_btn = ttk.Button(frame, text="Create new project", command=create_new_project)
frame.grid(row=0, column=0, padx=40, pady=40)
label.grid(row=1, column=0, columnspan=3)
open_existing_btn.grid(row=2, column=0, columnspan=1)
open_new_btn.grid(row=2, column=1, columnspan=1)
# "Open existing project" route views
browse_dir_btn = ttk.Button(frame, text="Browse project", command=browse_dir)

project_name = StringVar()
project_name_entry = ttk.Entry(frame, textvariable=project_name)
create_project_btn = ttk.Button(frame, text="Create", command=start)
prep_design_console = Text(frame, width=80, height=20)
proceed_btn = ttk.Button(frame, text="Proceed", command=proceed)
browse_file_btn = ttk.Button(frame, text="Add Verilog", command=browse_files)
next_btn = ttk.Button(frame, text="Next", command=begin_param_insertion)
upload_verilog_btn = ttk.Button(frame, text="Upload", command=upload_selected_verilog)

# Params insertion related views
clock_en = IntVar()
clock_en_check = ttk.Checkbutton(frame, text="Enable Clock", command=clk_metric_changed, variable=clock_en)

clk_period = StringVar()
clk_period_label = ttk.Label(frame, text="Clock Period:")
clk_period_entry = ttk.Entry(frame, textvariable=clk_period)

clk_port = StringVar()
clk_port_entry = ttk.Entry(frame, textvariable=clk_port)
clk_port_label = ttk.Label(frame, text="Clock Port Name:")

top_name = StringVar()
top_name_entry = ttk.Entry(frame, textvariable=top_name)
top_name_label = ttk.Label(frame, text="Verilog Top Name:")
begin_run_btn = ttk.Button(frame, text="Begin", command=begin_openlane_run)
root.mainloop()
