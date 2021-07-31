import os
import subprocess
from sys import stderr, stdout
from tkinter import *
from tkinter import ttk
from subprocess import call, run
import docker
from docker.api import volume

pdk_root = ""
openlane_root = ""

def start():
    project_name_entry.grid_forget()
    create_project_btn.grid_forget()
    label.configure(text="Creating your project please wait..")
    root.after(1, create_design)

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

def add_verilog_file():
    pass

def proceed():
    prep_design_console.grid_forget()
    proceed_btn.grid_forget()
    label.configure(text="Upload your verilog files")
    add_verilog_btn.grid(row=2, columnspan=3)

def upload_verilog_files():

    pass

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
project_name = StringVar()
project_name_entry = ttk.Entry(frame, textvariable=project_name)
create_project_btn = ttk.Button(frame, text="Create", command=start)
prep_design_console = Text(frame, width=80, height=20)
proceed_btn = ttk.Button(frame, text="Proceed", command=proceed)
add_verilog_btn = ttk.Button(frame, text="Add Verilog", command=upload_verilog_files)
root.mainloop()
