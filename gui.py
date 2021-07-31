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

def create_design(entryField):
    print("entry is " + entryField.get())
    print(openlane_root)
    client = docker.from_env()
    container = client.containers.run('efabless/openlane:current', command='./flow.tcl -design ' + entryField.get() + ' -init_design_config', 
        volumes={openlane_root: {'bind': '/openLANE_flow', 'mode': 'rw'},
                 pdk_root: {'bind': pdk_root, 'mode':'rw'}},
        environment=["PDK_ROOT=" + pdk_root],
        user=1001,
        detach=True,
        stdout=True,
        stderr=True)

    text = Text(frame, width=80, height=20)
    text.insert('1.0', container.logs().decode('utf-8'))
    text.grid(row=3, column=0)
def create_new_project():

    print("creating new project...")
    if read_env_variables() == True:
        label.configure(text="Set a name for the project")
        open_existing_btn.grid_forget()
        open_new_btn.grid_forget()
        project_name = StringVar()
        project_name_entry = ttk.Entry(frame, textvariable=project_name)
        project_name_entry.grid(row=2, column=0)
        create_project_btn = ttk.Button(frame, text="Create", command= lambda: create_design(project_name))
        create_project_btn.grid(row=2, column=1)
    else:
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
root.mainloop()
