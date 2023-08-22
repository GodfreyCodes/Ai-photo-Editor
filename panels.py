import customtkinter as ctk
from customtkinter import filedialog
from PIL import Image
import tensorflow as tf
from settings import *

AI_MODELS = ['None', 'Real-ESRGAN', 'ESRGAN', 'SRGAN', 'RDN']
AI_OPTIONS = ['None', 'AI Upscale 2x', 'AI Upscale 4x', 'AI Upscale 8x']

imported_image = None



class Panel (ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, fg_color = DARK_GREY)
        self.pack(fill = 'x', pady = 4, ipady =8)

class SliderPanel(Panel):
    def __init__(self, parent, text, data_var, min_value, max_value):
        super().__init__(parent = parent)

        # layout
        self.rowconfigure((0,1), weight = 1)
        self.columnconfigure(0, weight = 1)

        self.data_var = data_var
        self.data_var.trace('w', self.update_text)
        
        ctk.CTkLabel(self, text = text).grid(column =0, row =0, sticky = 'w', padx = 5)
        self.num_label =  ctk.CTkLabel(self, text = data_var.get())
        self.num_label.grid(column =1, row =0, sticky = 'E', padx = 5)
        
        ctk.CTkSlider(self, 
        fg_color= SLIDER_BG, 
        variable = self.data_var,
        from_ = min_value,
        to = max_value).grid(row =1, column = 0, columnspan =2, sticky = 'ew', padx = 5, pady = 5)

    def update_text(self, *args):
        self.num_label.configure(text = f'{round(self.data_var.get(), 2)}' )

class SegmentedPanel(Panel):
    def __init__(self, parent, text, data_var, options):
        super().__init__(parent = parent)

        ctk.CTkLabel(self, text = text).pack()
        ctk.CTkSegmentedButton(self, variable = data_var, values = options).pack(expand = True, fill = 'both', padx = 4, pady = 4)

class SwitchPanel(Panel):
    def __init__(self, parent, *args): #(text, data_var):
        super().__init__(parent = parent)

        for var, text in args:
            switch = ctk.CTkSwitch(self, text = text, variable = var, button_color = BLUE, fg_color = SLIDER_BG)
            switch.pack(side = 'left', expand = True, fill = 'both', padx = 5, pady = 5)     

class FileNamePanel(Panel):
    def __init__(self, parent, name_string, file_string):
        super().__init__(parent = parent)

        # data
        self.name_string = name_string
        self.name_string.trace('w', self.update_text)
        self.file_string = file_string

        # layout for file format
        ctk.CTkEntry(self, textvariable = self.name_string).pack(fill = 'x', padx = 20, pady = 5)
        frame = ctk.CTkFrame(self, fg_color = 'transparent')
        jpg_check = ctk.CTkCheckBox(frame, text = 'jpg', variable= self.file_string,command= lambda: self.click('jpg'), onvalue = 'jpg', offvalue = 'png')
        jpg_check.pack(side = 'left', fill = 'x', expand = True)
        png_check = ctk.CTkCheckBox(frame, text = 'png', variable= self.file_string,command= lambda: self.click('png') , onvalue = 'png', offvalue = 'jpg')
        png_check.pack(side = 'left', fill = 'x', expand = True)
        frame.pack(expand = True, fill = 'x', padx = 20)

        # preview text
        self.output = ctk.CTkLabel(self, text = '')
        self.output.pack()

    def click(self, value):
        self.file_string.set(value)
        self.update_text()

    def update_text(self, *args):
        if self.name_string.get():
            text = self.name_string.get().replace(' ', '_')
            self.output.configure(text = f'{text}.{self.file_string.get()}')

class FilePathPanel(Panel):
    def __init__(self, parent, path_string):
        super().__init__(parent = parent)

        # data
        self.path_string = path_string

        # layout
        ctk.CTkButton(self, text = 'Open Explorer', command = self.open_file_dialog).pack(pady = 5)
        ctk.CTkEntry(self, textvariable= self.path_string).pack(expand = True, fill = 'both', padx = 5, pady = 5)

    def open_file_dialog(self):
        self.path_string.set(filedialog.askdirectory())

class DropDownPanel (ctk.CTkOptionMenu):
    def __init__(self, parent, data_var, options):
        super().__init__(
            master = parent, 
            values = options,
            fg_color= DARK_GREY,
            button_color = DROPDOWN_MAIN_COLOR,
            button_hover_color= DROPDOWN_HOVER_COLOR ,
            dropdown_fg_color= DROPDOWN_MENU_COLOR,
            variable = data_var,)
        self.pack(fill = 'x', pady = 4)

class RevertButton(ctk.CTkButton):
    def __init__(self, parent, *args):
        super().__init__(
            master = parent,
            text = 'Revert',
            command = self.revert)
        self.pack(side = 'bottom', pady = 10)
        self.args = args

    def revert(self):
        for var, value in self.args:
            var.set(value)



class ColorFrame(ctk.CTkFrame):
    def __init__(self, parent, color_vars, model_vars, option_vars, imported_image):
        super().__init__(parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        model_CTkLabel = ctk.CTkLabel(self, text="Select AI Model:", justify='left', anchor="w")
        model_CTkLabel.pack()
        model_dropdown = DropDownPanel(self, model_vars['Model'], AI_MODELS)

        option_CTkLabel = ctk.CTkLabel(self, text="Select Upscale Option:", justify='left', anchor="w")
        option_CTkLabel.pack()
        option_dropdown = DropDownPanel(self, option_vars['Upcaler'], AI_OPTIONS)

        result_label = ctk.CTkLabel(self, text="")
        result_label.pack()

        run_upscale_button = RunAiButton(self, imported_image, model_vars, option_vars, result_label)
        run_upscale_button.pack()

        save_upscale_button = SaveAiButton(self, upscaled_image, result_label)
        save_upscale_button.pack()  




class RunAiButton(ctk.CTkButton):
    def __init__(self, parent, imported_image, model_vars, option_vars, result_label):
        super().__init__(
            master=parent,
            text='Run AI Upscaler',
            command=self.run_upscale)
        self.pack(side='top', pady=10)

        self.imported_image = imported_image
        self.model_vars = model_vars
        self.option_vars = option_vars
        self.result_label = result_label

    def run_upscale(self):
        selected_model = self.model_vars['Model'].get()
        selected_option = self.option_vars['Upcaler'].get()

        if selected_model == 'None' or selected_option == 'None':
            self.result_label.configure(text="Please select both model and option.")
            return

        image = self.imported_image    
        upscale_factor = int(selected_option.split()[-1][0])
        
         # Perform AI upscaling using the selected model and option

        upscaled_image = self.perform_upscale(self.imported_image, upscale_factor)        

        
        # Update the upscaled image label
        self.display_upscaled_image(upscaled_image)

        self.result_label.configure(text="Upscaling complete.")

    def perform_upscale(self, image, upscale_factor):
        selected_model = self.model_vars['Model'].get()
        selected_option = self.option_vars['Upcaler'].get()
        
        # Perform AI upscaling using the selected model and option
        model_vars = {'Model': ctk.StringVar(value=AI_OPTIONS[0])}
        model_panel = DropDownPanel(self, model_vars['Model'], AI_MODELS)  # Pass AI_MODELS as the third argument
        model_vars.setdefault(self, model_vars['Model'], AI_MODELS[0])
        model_vars.dropdown = ctk.CTkOptionMenu(model_panel, model_vars['Model'], AI_MODELS)
        model_vars.dropdown.pack()


        option_vars = {'Upcaler': ctk.StringVar(value=AI_OPTIONS[0])}
        option_panel = DropDownPanel(self, option_vars['Upcaler'], AI_OPTIONS)  # Pass AI_OPTIONS as the third argument
        option_vars.setdefault(self, option_vars['Upcaler'], AI_OPTIONS[0])
        option_vars.DropDownPanel = ctk.CTkOptionMenu(option_panel, option_vars['Upcaler'], AI_OPTIONS)
        option_vars.DropDownPanel.pack()

        upscaled_image = image.resize((image.width * upscale_factor, image.height * upscale_factor), Image.LANCZOS)
        return upscaled_image
        

    
    def display_upscaled_image(self, image):
        # Clear previous upscaled image (if any)
        if hasattr(self, 'upscaled_image_label'):
            self.upscaled_image_label.destroy()
    
        # Display the upscaled image on the UI
        self.upscaled_image_label = ctk.CTkLabel(self, image=ImageTk.PhotoImage(image))
        self.upscaled_image_label.pack(side='top', padx=10, pady=10)





class SaveAiButton(ctk.CTkButton):
    def __init__(self, parent, image_to_save, result_label):
        super().__init__(
            master=parent,
            text='Save AI Upscaled Image',
            command=self.save_image)
        self.pack(side='top', pady=10)

        self.image_to_save = image_to_save  # Use the instance variable
        self.result_label = result_label

    def save_image(self):
        if self.image_to_save is None:
            self.result_label.configure(text="No upscaled image available to save.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not output_path:
            return  # User canceled save dialog

        self.image_to_save.save(output_path)  # Use the instance variable
        self.result_label.configure(text="Image saved successfully.")






class SaveButton(ctk.CTkButton):
    def __init__(self, parent, export_image, name_string, file_string, path_string):
        super().__init__(
            master = parent,
            text = 'Save',
            command = self.save)
        self.pack(side = 'bottom', pady = 10)

        self.export_image = export_image
        self.name_string = name_string
        self.file_string = file_string
        self.path_string = path_string

    def save(self):
        self.export_image(
            self.name_string.get(),
            self.file_string.get(),
            self.path_string.get()
        )