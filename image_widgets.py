import customtkinter as ctk
import subprocess
import sys
from tkinter import filedialog, Canvas
from settings import *

class ImageImport(ctk.CTkFrame):
    def __init__(self, parent, import_func):
        super().__init__(master = parent)
        self.grid(column = 0, columnspan = 2,  row = 0, sticky = 'nsew')
        self.import_func = import_func

        ctk.CTkButton(self, text = 'open image', command = self.open_dialog).pack(expand =True)

    def open_dialog(self):
        path = filedialog.askopenfile().name
        self.import_func(path)



class ImageGen(ctk.CTkFrame):
    def __init__(self, parent, script_path, form_window):
        super().__init__(master = parent)
        self.grid(column= 0, columnspan= 2, row=1, sticky= 'nsew')
        self.script_path = script_path
        self.form_window = form_window

        ctk.CTkButton(self, text= 'Generate Image', command = self.run_script,).pack(expand=True)

    def run_script(self):
        try:

             # Hide the main window
            self.master.withdraw()

            subprocess.run(["python", self.script_path], check=True)
        except subprocess.CalledProcessError as e:
            print("Error:", e)
        else:
            #self.form_window.destroy()
            sys.exit()  # Exit main.py application
            

class ImageOutput(Canvas):
    def __init__(self, parent, resize_image):
        super().__init__(master = parent, background = BACKGROUND_COLOR, bd =0, highlightthickness = 0, relief = 'ridge')
        self.grid(row = 0, column = 1, sticky = 'nsew', padx = 10, pady =10)
        self.bind('<Configure>', resize_image)

class CloseOutput(ctk.CTkButton):
    def __init__(self, parent, close_func):
        super().__init__(
            master = parent, 
            command = close_func,
            text = 'X', 
            text_color = WHITE, 
            fg_color = 'transparent', 
            width = 40, 
            height = 40,
            corner_radius= 0,
            hover_color= CLOSE_RED
            )
        self.place(relx = 0.99, rely = 0.01, anchor = 'ne')