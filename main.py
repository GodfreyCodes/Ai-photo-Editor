import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import socket
import sys
import os
import realesrgan
from image_widgets import *
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
import tensorflow as tf
from menu import Menu
from panels import *
from settings import *

class App(ctk.CTk):
     def __init__(self):

        #  setup
        super().__init__() 
        ctk.set_appearance_mode('dark') 
        self.geometry('1000x600')
        self.title('Romera Editor')
        self.minsize(800., 500)
        self.init_parameters()
        self.upscaled_image = None
        self.form_window = None

        # layout
        self.rowconfigure(0, weight = 1) 
        self.columnconfigure(0, weight = 2, uniform='a') 
        self.columnconfigure(1, weight = 6, uniform='a')

        # canvas data
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
    
        # widgets
        self.image_import = ImageImport(self, self.import_image) # ImageImport (Frame with a button)
        self.image_gen = ImageGen(self, 'maingenimg.py',  self.form_window) #  ImageGen (Frame with a button)
      
       
        # run
        self.mainloop()
     
     def init_parameters(self):
        self.pos_vars ={
            'rotate': ctk.DoubleVar(value = ROTATE_DEFAULT),
            'zoom' : ctk.DoubleVar(value = ZOOM_DEFAULT),
            'flip' : ctk.StringVar(value = FLIP_OPTIONS[0])}
        
        self.color_vars = {}

        self.model_vars = {
          'Model': ctk.StringVar(value = AI_MODELS[0]),}

        self.option_vars = {
          'Upcaler': ctk.StringVar(value = AI_OPTIONS[0]),}
        
        self.effect_vars = {
          'grayscale': ctk.BooleanVar(value = GRAYSCALE_DEFAULT),
          'invert': ctk.BooleanVar(value = INVERT_DEFAULT),
          'brightness': ctk.DoubleVar(value = BRIGHTNESS_DEFAULT),
          'vibrance': ctk.DoubleVar(value = VIBRANCE_DEFAULT),
          'blur': ctk.DoubleVar(value = BLUR_DEFAULT),
          'contrast': ctk.IntVar(value = CONTRAST_DEFAULT),
          'effect': ctk.StringVar(value = EFFECT_OPTIONS[0]),}

        # tracing
        combined_vars = list(self.pos_vars.values()) + list(self.color_vars.values()) + list(self.effect_vars.values())
        for var in combined_vars:
          var.trace('w', self.manipulate_image)

     def manipulate_image(self, *args):
        self.image = self.original
        
        #rotate
        if self.pos_vars['rotate'].get() != ROTATE_DEFAULT:
          self.image = self.image.rotate(self.pos_vars['rotate'].get())

        #
        if self.pos_vars['zoom'].get() != ZOOM_DEFAULT:
          self.image =  ImageOps.crop(image = self.image, border = self.pos_vars['zoom'].get())

        #flip
        if self.pos_vars['flip'].get() != FLIP_OPTIONS[0]:
         if self.pos_vars['flip'].get() == 'X':
          self.image = ImageOps.mirror(self.image)
         if self.pos_vars['flip'].get() == 'Y':
          self.image = ImageOps.flip(self.image)
         if self.pos_vars['flip'].get() == 'Both':
          self.image = ImageOps.flip(ImageOps.mirror(self.image))

        # brightness & vibrance
        if self.effect_vars['brightness'].get() != BRIGHTNESS_DEFAULT or self.effect_vars['vibrance'].get() != VIBRANCE_DEFAULT:
          brightness_enhancer = ImageEnhance.Brightness(self.image)
          self.image = brightness_enhancer.enhance(self.effect_vars['brightness'].get())
          vibrance_enhancer = ImageEnhance.Color(self.image)
          self.image = vibrance_enhancer.enhance(self.effect_vars['vibrance'].get())

        # grayscale and invert of the colors
        if self.effect_vars['grayscale'].get() or self.effect_vars['invert'].get():
          self.image = ImageOps.grayscale(self.image) if self.effect_vars['grayscale'].get() else self.image

          self.image = ImageOps.invert(self.image) if self.effect_vars['invert'].get() else self.image

        # blur & contrast
        if self.effect_vars['blur'].get() != BLUR_DEFAULT or self.effect_vars['contrast'].get() != CONTRAST_DEFAULT:
          self.image = self.image.filter(ImageFilter.GaussianBlur(self.effect_vars['blur'].get()))
          self.image = self.image.filter(ImageFilter.UnsharpMask(self.effect_vars['contrast'].get()))

        # effect
        match self.effect_vars['effect'].get():
          case 'Emboss': self.image = self.image.filter(ImageFilter.EMBOSS)
          case 'Find edges': self.image = self.image.filter(ImageFilter.FIND_EDGES)
          case 'Contour': self.image = self.image.filter(ImageFilter.CONTOUR)
          case 'Edge enhance': self.image = self.image.filter(ImageFilter.EDGE_ENHANCE)
      
                
        self.place_image()

     def import_image(self, path):
        self.original = Image.open(path)
        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)
      
      # hide the image import widget
        self.image_import.grid_forget()
        self.image_gen.grid_forget()
        self.image_output = ImageOutput(self, self.resize_image)
        self.close_button = CloseOutput(self, self.close_edit)

        self.menu = Menu(self, self.pos_vars, self.color_vars, self.effect_vars, self.export_image, self.model_vars, self.option_vars, self.import_image)

     def close_edit(self):
        self.image_output.grid_forget()
        self.close_button.place_forget()
        self.image_import = ImageImport(self, self.import_image)
        self.image_gen = ImageGen(self, 'maingenimg.py',  self.form_window)

        self.menu.grid_forget()   

     def resize_image(self,event):

          # current canvas ratio
        canvas_ratio = event.width / event.height

        # update canvas attributes
        self.canvas_width = event.width
        self.canvas_height = event.height

          #resize image
        if canvas_ratio > self.image_ratio: # the canvas is wider than the image
          self.image_height = int(event.height)
          self.image_width = int(self.image_height * self.image_ratio)
        else: # the canvas is taller than the image
          self.image_width = int(event.width)
          self.image_height = int(self.image_width / self.image_ratio)

        self.place_image()

     def place_image(self):
        self.image_output.delete('all')
        resized_image = self.image.resize((self.image_width, self.image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(self.canvas_width / 2,self.canvas_height / 2, image = self.image_tk)

     def export_image(self, name, file, path):
        export_string = f'{path}/{name}.{file}'
        self.image.save(export_string)

     def run_upscale(self, parent, imported_image, model_vars, option_vars, result_label):
        selected_model = model_vars['Model'].get()
        selected_option = option_vars['Upcaler'].get()

        if selected_model == 'None' or selected_option == 'None':
            result_CTklabel.configure(text="Please select both model and option.")
            return

        try:
            # Load your original image (self.image) here
            upscaled_image = perform_upscaling(self.imported_image, selected_model, selected_option)

            # Display the upscaled image using upscaled_image_label
            upscaled_image_label.configure(image=ImageTk.PhotoImage(upscaled_image))
            self.result_label.configure(text="Upscaling complete.")
            
            # Add any additional UI updates or processing you need here
        except ValueError as e:
            result_CTklabel.configure(text=str(e))

     def save_upscaled_image(self, result_CTklabel):
        if self.upscaled_image is None:
            result_CTklabel.configure(text="No upscaled image available to save.")
            return


def close_image_gen(self): #work in progress
        # Do not hide the ImageGen widget

        # Close the form window if it's open
        if self.form_window:
            self.withdraw()
            #.form_window.destroy()
            #self.form_window = None


def init_ui(self):
        # Load the initial image
        self.image = Image.open(path)  # Replace with your image path
        self.displayed_image = ImageTk.PhotoImage(self.image)

        self.image_label = tk.Label(self.image_frame, image=self.displayed_image)
        self.image_label.pack()

        # Create variables to hold dropdown selections
        color_vars = {
            "Model": ctk.StringVar(self.root),
            "Colorization Option": ctk.StringVar(self.root),
        }

        model_vars = {
            "Colorizer": ctk.StringVar(self.root),
            "Upscaler": ctk.StringVar(self.root),
        }

        option_vars = {
            "Colorization Option": ctk.StringVar(self.root),
            "Upcale Option": ctk.StringVar(self.root),
        }

        # Create ColorFrame instances
        color_frame = panels.ColorFrame(self.image_frame, color_vars, model_vars, option_vars, self.image_label)

        # Add ColorFrame and UpscaleTab to the notebook
        self.notebook.add(color_frame, text="Colorize")
        upscale_tab = panels.UpscaleTab(self.image_frame, color_vars, model_vars, option_vars, self.image_label)
        self.notebook.add(upscale_tab, text="Upscale")

            

App()