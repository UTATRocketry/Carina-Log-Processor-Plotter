
from typing import Any
from customtkinter import *
from pandas import DataFrame
import tkinter as tk

class OptionsColumn(CTkFrame):
    def __init__(self, *args, master: Any, values: list = [], addcommand = None, removecommmand = None, ctype: str = "S", padx:int = 0, pady:int = 0, font:tuple = ("Arial", 14), **kwargs)->None:
        super().__init__(*args, master=master, **kwargs)

        self.num_boxes = 2
        self.values = values
        self.padx = padx
        self.pady = pady
        self.font = font
        self.type = ctype
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(self.get_row_tuple(), weight=1)
        if addcommand is None:
            self.addcommand = self.add_option
        else:
            self.addcommand = addcommand
        if removecommmand is None:
            self.removecommand = self.remove_option
        else:
            self.removecommand = removecommmand

        opt = CTkOptionMenu(self, font=self.font, values=["None"] + self.values, anchor="center", command=self.update_boxes)
        opt.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky = "ew")
        self.option_boxes = [opt]
        self.addbutton = CTkButton(master=self, text="+", font=self.font, width = 30, command=self.addcommand)
        self.addbutton.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.removebutton = CTkButton(master=self, text="-", font=self.font, width = 30, fg_color="darkred", hover_color="red", command=self.removecommand)
        self.removebutton.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    def add_option(self)->None:
        if self.option_boxes[self.num_boxes - 2].get() != "None" and len(self.available_choices()) > 1:
            new_opt = CTkOptionMenu(self, font=self.font, values=self.available_choices(), anchor="center")
            new_opt.grid(row=self.num_boxes - 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
            self.option_boxes.append(new_opt)
            self.num_boxes += 1
            self.grid_rowconfigure(self.get_row_tuple(), weight=1)
            self.addbutton.grid(row=self.num_boxes - 1, column=0, padx=5, pady=5, sticky="ew")
            self.removebutton.grid(row=self.num_boxes - 1, column=1, padx=5, pady=5, sticky="ew")
            self.update()

    def remove_option(self)->None:
        if len(self.option_boxes) > 1:
            last_box = self.option_boxes.pop()
            last_box.destroy()
            self.num_boxes -= 1
            self.grid_rowconfigure(self.get_row_tuple(), weight=1)
            self.addbutton.grid(row=self.num_boxes - 1, column=0, padx=5, pady=5, sticky="ew")
            self.removebutton.grid(row=self.num_boxes - 1, column=1, padx=5, pady=5, sticky="ew")
            self.update()

    def get_row_tuple(self)->tuple:
        res = ()
        for i in range(self.num_boxes):
            res = (*res, i)
        return res
    
    def available_choices(self)->list:
        res = ["None"]
        already_chosen = [name.get() for name in self.option_boxes]
        if self.type == "S":
            if already_chosen[0] != "None":
                if "MFR" == already_chosen[0][0]:
                    letter = "F"
                elif "M" == already_chosen[0][0]:
                    letter = "M"
                elif "P" == already_chosen[0][0]:
                    letter = "P"
                for name in self.values:
                    if letter == name[0] and name != "MFR" and name not in already_chosen: 
                        res.append(name)
            else:
                res += self.values 
        else:
            for name in self.values:
                if name not in already_chosen: res.append(name)
        return res

    def update_boxes(self, choice)->None:
        self.option_boxes[0].set(choice)
        if len(self.option_boxes) > 1:
            for box in self.option_boxes[1:]:
                box.configure(values=self.available_choices())
                box.set("None")
                
    def selections(self)->list:
        selection = []
        for box in self.option_boxes:
            if box.get() != "None": 
                selection.append(box.get())
        return selection

class ActuatorTimeDropdown(CTkFrame): 
    def __init__(self, *args, master: Any, actuator_df:DataFrame, entry_boxes:list[CTkEntry, CTkEntry], text:str, padx:int = 0, pady:int = 0, font:tuple = ("Arial", 16), **kwargs)->None:
        super().__init__(*args, master=master, **kwargs)

        self.df = actuator_df
        self.actuators = self.df.columns.to_list()[1:]
        self.entry_boxes = entry_boxes
        self.padx = padx
        self.pady = pady
        self.font = font
        self.text = text

        self.grid_columnconfigure((0, 1, 2), weight = 1)
        self.grid_rowconfigure((0), weight = 1)

        self.get_actuator_times()

        self.label = CTkLabel(self, text=self.text, font=self.font)
        self.actuator_opt = CTkOptionMenu(self, font=self.font, values=self.actuators, anchor="center", command=self.set_time_options)
        self.time_opt = CTkOptionMenu(self, font=self.font, values=self.actuation_times[self.actuator_opt.get()], anchor="center", command=self.set_entry_boxes)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.actuator_opt.grid(row=0, column=1, padx=(5, 5), pady=10, sticky="ew")
        self.time_opt.grid(row=0, column=2, padx=(5, 5), pady=10, sticky="ew")   
    
    def get_actuator_times(self, *args) -> None:
        self.actuation_times = {}
        for column in self.df.columns[1:]:
            changes = self.df[column].diff().fillna(0)
            switch_on = self.df['Time'][changes == 1].tolist()
            switch_off = self.df['Time'][changes == -1].tolist()

            res = []
            l = len(switch_off)
            for i in range(len(switch_on)):
                res.append(f'{switch_on[i]}s Off -> On')
                if i < l:
                    res.append(f'{switch_off[i]}s On -> Off')

            self.actuation_times[column] = res if res else [""]

    def set_time_options(self, choice:str)->None:
        self.time_opt.set("")
        self.time_opt.configure(values=self.actuation_times[choice])

    def set_entry_boxes(self, choice:str)->None:
        if choice != "":
            choice = choice.split("s ")[0]
            self.entry_boxes[0].delete(0, tk.END)
            self.entry_boxes[0].insert(0, choice.split("s ")[0])
            self.entry_boxes[1].delete(0, tk.END)
            for i in range(len(self.actuation_times[self.actuator_opt.get()])):
                if self.actuation_times[self.actuator_opt.get()][i].split("s ")[0] == choice:
                    break
            if i + 1 < len(self.actuation_times[self.actuator_opt.get()]):
                self.entry_boxes[1].insert(0, self.actuation_times[self.actuator_opt.get()][i + 1].split("s ")[0])
            

class OptionsBar(CTkFrame):
    def __init__(self, *args, master: Any, titles: list = [], choices: list = [], addcommand = None, removecommmand = None, padx:int = 0, pady:int = 0, font:tuple = ("Arial", 16), **kwargs)->None:
        super().__init__(*args, master=master, **kwargs)

        self.num_boxes = len(titles) + 2
        self.choices = choices
        self.padx = padx
        self.pady = pady
        self.font = font
        self.titles = titles
        self.option_boxes = []
        if addcommand is None:
            self.addcommand = self.add_box
        else:
            self.addcommand = addcommand
        if removecommmand is None:
            self.removecommand = self.remove_box
        else:
            self.removecommand = removecommmand

        self.grid_columnconfigure(self.get_column_tuple(), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        for i, title in enumerate(titles):
            t = CTkLabel(master=self, text=title, font=self.font, anchor="center")
            t.grid(row=0, column=i, padx=self.padx, pady=self.pady, sticky="nsew")
            self.last_title = t

        for i in range(self.num_boxes - 2):
            opt = CTkOptionMenu(master=self, font=self.font, values=self.choices, anchor="center")
            opt.grid(row=1, column=i, padx=5, pady=5, sticky="ew")
            self.option_boxes.append(opt)

        self.addbutton = CTkButton(master=self, text="+", font=self.font, width = 30, command=self.addcommand)
        self.addbutton.grid(row=1, column=self.num_boxes - 2, padx=5, pady=5, sticky="ew")
        self.removebutton = CTkButton(master=self, text="-", font=self.font, width = 30, fg_color="darkred", hover_color="red", command=self.removecommand)
        self.removebutton.grid(row=1, column=self.num_boxes - 1, padx=5, pady=5, sticky="ew")

    def add_box(self)->None:
        new_opt = CTkOptionMenu(master=self, font=self.font, values=self.choices, anchor="center")
        new_opt.grid(row=1, column=self.num_boxes - 2, padx=10, pady=5, sticky="ew")
        self.option_boxes.append(new_opt)
        self.num_boxes += 1
        self.grid_columnconfigure(self.get_column_tuple(), weight=1)
        self.addbutton.grid(row=1, column=self.num_boxes - 2, padx=5, pady=5, sticky="ew")
        self.removebutton.grid(row=1, column=self.num_boxes - 1, padx=5, pady=5, sticky="ew")
        self.last_title.grid(row=0, column=len(self.titles) - 1, columnspan=self.num_boxes, padx=self.padx, pady=self.pady, sticky="nsew")
        self.update()

    def remove_box(self):
        if self.num_boxes - 2 > len(self.titles):
            last_box = self.option_boxes.pop()
            last_box.destroy()
            self.num_boxes -= 1
            self.grid_columnconfigure(self.get_column_tuple(), weight=1)
            self.addbutton.grid(row=1, column=self.num_boxes - 2, padx=5, pady=5, sticky="ew")
            self.removebutton.grid(row=1, column=self.num_boxes - 1, padx=5, pady=5, sticky="ew")
            self.last_title.grid(row=0, column=len(self.titles) - 1, columnspan=self.num_boxes, padx=self.padx, pady=self.pady, sticky="nsew")
            self.update()

    def get_column_tuple(self) -> tuple:
        res = ()
        for i in range(self.num_boxes):
            res = (*res, i)
        return res

class RadioOptions(CTkFrame):
    pass # finsih later
        
