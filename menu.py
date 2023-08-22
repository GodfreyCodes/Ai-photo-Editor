import customtkinter as ctk
import tkinter as tk
from panels import  *

class Menu(ctk.CTkTabview):
    def __init__(self, parent, pos_vars, color_vars, effect_vars, export_image, model_vars, option_vars, imported_image):
        super().__init__(master = parent)
        self.grid(row = 0, column = 0, sticky = "nsew", pady = 10, padx = 10)

        #tabs
        self.add('Edit')
        self.add('Upscale')
        self.add('Effects')
        self.add('Export')

        # WIDGETS
        PositionFrame(self.tab('Edit'), pos_vars)
        ColorFrame(self.tab('Upscale'), color_vars, model_vars, option_vars, imported_image)
        EffectsFrame(self.tab('Effects'), effect_vars)
        ExportFrame(self.tab('Export'), export_image)

        #frames

class PositionFrame(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
        super().__init__(master = parent, fg_color ='transparent')
        self.pack(expand = True, fill = 'both')

        SliderPanel(self, 'Rotation', pos_vars['rotate'], 0, 360)
        SliderPanel(self, 'Zoom', pos_vars['zoom'], 0, 400)
        SegmentedPanel(self, 'Invert', pos_vars['flip'], FLIP_OPTIONS)
        RevertButton(self, 
                    (pos_vars['rotate'], ROTATE_DEFAULT),
                    (pos_vars['zoom'], ZOOM_DEFAULT),
                    (pos_vars['flip'], FLIP_OPTIONS[0]))



class EffectsFrame(ctk.CTkFrame):
    def __init__(self, parent, effect_vars):
        super().__init__(master = parent, fg_color ='transparent')
        self.pack(expand = True, fill = 'both')

        SwitchPanel(self, (effect_vars['grayscale'], 'B/W'),(effect_vars['invert'], 'Invert'))
        SliderPanel(self, 'Brightness', effect_vars['brightness'], 0, 5)
        SliderPanel(self, 'Vibrance', effect_vars['vibrance'], 0, 5)
        SliderPanel(self, 'Blur', effect_vars['blur'], 0, 30)
        SliderPanel(self, 'Contrast', effect_vars['contrast'], 0, 10)
        DropDownPanel(self, effect_vars['effect'], EFFECT_OPTIONS)


        RevertButton(self, 
                    (effect_vars['grayscale'], GRAYSCALE_DEFAULT),
                    (effect_vars['invert'], INVERT_DEFAULT),
                    (effect_vars['brightness'], BRIGHTNESS_DEFAULT),
                    (effect_vars['vibrance'], VIBRANCE_DEFAULT),
                    (effect_vars['blur'], BLUR_DEFAULT),
                    (effect_vars['contrast'], CONTRAST_DEFAULT),
                    (effect_vars['effect'], EFFECT_OPTIONS[0]))

class ExportFrame(ctk.CTkFrame):
    def __init__(self, parent, export_image):
        super().__init__(master = parent, fg_color ='transparent')
        self.pack(expand = True, fill = 'both')

        #data
        self.name_string = ctk.StringVar()
        self.file_string = ctk.StringVar(value = 'jpg')
        self.path_string = ctk.StringVar()

        #widgets
        FileNamePanel(self, self.name_string, self.file_string)
        FilePathPanel(self, self.path_string)
        SaveButton(self, export_image, self.name_string, self.file_string, self.path_string)