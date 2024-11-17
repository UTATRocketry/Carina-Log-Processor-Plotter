
import os
import pandas as pd
import matplotlib.pyplot as plt
import time as t
from customtkinter import *
from tkinter import messagebox
from datetime import datetime


def textbox_caller(func, folder_opt: CTkOptionMenu, plot: IntVar, save: IntVar):
    '''This function is used by the start screen button and takes the entry box to get the folder name. 
    It then cals the function with the folder name parameter andf wehther to save th eplot or not'''
    def call_func():
        text = folder_opt.get()
        folder = os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", text, "raw")
        append_to_log(f'Begining data parsing in {folder}', "INFO")
        func(text, plot.get(), save.get())
    return call_func

def replot_caller(func, start_box: CTkEntry, end_box: CTkEntry, save: IntVar):
    '''Takes in inputs from ui and calls function to replot all graphswith parameters'''
    def call_func2():
        try:
            start = start_box.get()
            end = end_box.get()
            if start == "" and end == "":
                func()
            elif start == "":
                func(end=float(end))
            elif end == "":
                func(start=float(start))
            else:
                start = float(start)
                end = float(end)
                if start > end:
                    gui_error("End time cannot be less then Start time")
                    append_to_log(f"Failed to create graphs as start time was greater then end time (start:{start}, end:{end})", "ERROR")
                    return
                func(start, end, save.get())
        except Exception as e:
            gui_error("Invalid Start or End Time")
            append_to_log(f"Failed to replot all graphs due to {e}", "ERROR")
    return call_func2

def custom_plot_caller(func, times:tuple[CTkEntry, CTkEntry], options:tuple, save: IntVar, plot_name: CTkEntry): 
    '''Takes inpout from ui and calls custom plot function feeding it the parameters it needs'''
    def call_func2():
        try:
            choices = (options[0].selections(), options[1].selections(), options[2].selections())
            name = plot_name.get() if plot_name.get() != "" else None
            start = times[0].get()
            end = times[1].get()
            if start == "" and end == "":
                func(choices, save=save.get(), plot_name=name)
            elif start == "":
                func(choices, end=float(end), save=save.get(), plot_name=name)
            elif end == "":
                func(choices, start=float(start), save=save.get(), plot_name=name)
            else:
                if start > end:
                    gui_error("End cannot be less then Start")
                    append_to_log(f"Failed to create custom graph as start time was greater then end time (start:{start}, end:{end})", "ERROR")
                    return
                func(choices, float(start), float(end), save.get(), plot_name=name)
        except Exception as e:
            gui_error("Invalid Start or End value")
            append_to_log(f"Failed to create custom graph due to {e}", "ERROR")
    return call_func2

def engine_calc_caller(func, times:tuple[CTkEntry, CTkEntry], masses:tuple[CTkEntry, CTkEntry], save: IntVar, text_box: CTkTextbox):
    '''Takes entry from ui and calls function with the values, used foe engine calc function'''
    def call_func3():
        try:
            wet_mass = float(masses[0].get())
            dry_mass = float(masses[1].get())
            if times[0].get() == '':
                start_time = 0
            else:
                start_time = float(times[0].get())
            if times[1].get() == '':
                func(text_box, wet_mass, dry_mass, start_time, save=save.get())
            else:
                if start_time > float(times[1].get()):
                    gui_error("End cannot be less then Start")
                    append_to_log(f"Failed to run engine calculations as end time was smaller then start time", "ERROR")
                    return
                func(text_box, wet_mass, dry_mass, start_time, float(times[1].get()), save=save.get())
        except Exception as e:
            gui_error("One of your inputs for engine calculation is invalid")
            append_to_log(f"Failed to run engine calculations due to {e}", "ERROR")
    return call_func3

def custom_dataset_caller(func, frame:CTkFrame, entry:CTkEntry):
    '''Takes the entrys from UI and calls function with the values from entries'''
    def call_func4():
        tup = frame.get()
        if tup[0] == "" or tup[1] == "":
            gui_error("One of your data inputs is invalid")
            append_to_log("One of the inputs for making a new dataset was incorrect", "ERROR")
            return
        if entry.get() == "":
            gui_error("Dataset Name cannot be null")
            append_to_log("Name for new dataset cannot be null, breaking process", "ERROR")
            return
        else:
            func([tup[0], tup[1]], tup[2], entry.get())
    return call_func4

def gui_error(msg: str) -> None:
    '''Causes error pop up window with the provided message'''
    messagebox.showerror(title="Program Error", message=msg)
    append_to_log(msg, "ERROR")

def gui_popup(msg:str) -> None:
    '''Creates window pop up with given message'''
    messagebox.showinfo(title="Program Info", message=msg)
    append_to_log(msg)

def clear_gui(window: CTk) -> None:
    '''Clears the entire window provided of all visual elements'''
    for child in window.children.copy():
        window.children[child].destroy() 
    append_to_log("Clearing GUI Screen", "INFO") 


def single_plot(folder_name: str, time:list, left_axis: list, right_axis:list, actuators:list, save:int = 0, plot_name = None) -> None: 
    '''genertes a singular plot but can plt mutliple lines and actuators actuaion times as asymptotes'''
    if not os.path.exists(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", folder_name, "Plots"))

    colors = ['b','g','r','c','m','y','k']
    if plot_name is not None:
        name = plot_name
    else:
        name = ""
        for tup in left_axis: #fix
            name += tup[0] + " & "
        for tup in right_axis:
            name += tup[0] + " & "
        for tup in actuators:
            name += tup[0] + " & "
        name += "Vs Time"

    fig = plt.figure(name)
    i = 0
    max_val = 0
    min_val = 0
    plotted = True
    if left_axis and right_axis:
        for sensor in left_axis:
            plt.plot(time, sensor[1], label=sensor[0], color=colors[i])
            min_val, max_val = max_min_check(min_val, max_val, sensor[1])
            i += 1
        plt.ylabel(get_units(sensor[0]))
        ax2 = plt.twinx()
        for sensor in right_axis:
            ax2.plot(time, sensor[1], label=sensor[0], color=colors[i])
            min_val, max_val = max_min_check(min_val, max_val, sensor[1])
            i += 1
        ax2.set_ylabel(get_units(sensor[0]))
    elif left_axis:
        for sensor in left_axis:
            plt.plot(time, sensor[1], label=sensor[0], color=colors[i])
            min_val, max_val = max_min_check(min_val, max_val, sensor[1])
            i += 1
        plt.ylabel(get_units(sensor[0]))
    elif right_axis: 
        for sensor in right_axis:
            plt.plot(time, sensor[1], label=sensor[0], color=colors[i])
            min_val, max_val = max_min_check(min_val, max_val, sensor[1])
            i += 1
        plt.ylabel(get_units(sensor[0]))
    else:
        plotted = False
    
    i = len(colors) - 1
    if actuators and plotted:
        for actuator in actuators:
            actuations = get_actuation_indexes(actuator[1])
            for actuation in actuations:
                new_xaxis = [time[actuation[0]]]*2
                color = colors[i]
                plt.plot(new_xaxis, [min_val - 2, max_val + 2], label=f'{actuator[0]} {actuation[1]}', color=colors[i], linestyle='-.')
                i -= 1
                if i < 0:
                    i = len(colors) - 1
    elif actuators:
        for actuator in actuators:
            plt.plot(time, actuator[1], color=colors[i], label=actuator[0])
            i += 1
        plt.ylabel("On/Off (1 or 0)")

    plt.xlabel("Time (s)")
    plt.grid()
    plt.title(name)
    fig.legend()
    fig.show()

    if save == 1:
        fig.savefig(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", folder_name, "Plots", f"{name} {t.strftime('%Hh%Mm%Ss', t.gmtime(time[0]))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(time[-1]))}.jpg"), dpi=fig.dpi)

def max_min_check(prev_min: float, prev_max: float, data: list)->tuple:
    '''returns maximum and minimum value of a dataset and compares it to old maximums and minimums provided and returns whatever is lowest'''
    cur_max = -1000
    cur_min = 1000
    for value in data:
        if value > cur_max:
            cur_max = value
        if value < cur_min:
            cur_min = value
    res1, res2 = prev_min, prev_max
    if cur_max > prev_max:
        res2 = cur_max
    if cur_min < prev_min:
        res1 = cur_min
    return res1, res2

def generate_plots(folder_name: str, dataframe: pd.DataFrame, type: str = "sensor", start_time = 0, end_time = None, save:int = 0) -> None:
    '''generates a plot for each element in the dataframe between the start and end time'''
    if not os.path.exists(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", folder_name, "Plots"))

    time = dataframe["Time"].to_list()
    start = get_xaxis_index(time, start_time)
    end = get_xaxis_index(time, end_time)
    if start == end: start -= 1
    time = time[start:end]
    if type.lower() == "actuator":
        time.append(time[-1] + 0.01)
    for column in dataframe.columns:
        if column != "Time":
            p = plt.figure(column + " vs Time Plot")
            data = dataframe[column].to_list()[start:end]
            if type.lower() == "sensor":
                plt.plot(time, data)
            elif type.lower() == "actuator":
                plt.stairs(data, time)
            plt.grid()
            plt.title(column + " vs Time Plot")
            plt.xlabel("Time (s)")
            plt.ylabel(column + " " + get_units(column))
            p.show() 
            if save == 1:
                p.savefig(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", folder_name, "Plots", f"{column} vs Time Plot T[{t.strftime('%Hh%Mm%Ss', t.gmtime(start_time))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(end_time))}].jpg"), dpi=p.dpi)

def get_xaxis_index(xaxis: list, given_time) -> int:
    '''Returns index of the closest value in a dataset to the provided value'''
    if given_time == 0:
        return given_time
    elif given_time is None:
        return len(xaxis)
    if given_time and given_time < 0:
        return 0
    else:
        for i, t in enumerate(xaxis):
            if t > given_time:
                return i - 1
    return i
            
def get_units(name: str)->str:
    '''Returns a string representing units based off the name of the data sensor provided'''
    unit = name[0]
    if "BV" in name or "SV" in name or unit == "E":
        return "On/Off"
    elif unit == "P":
        return "Pressure (psi)"
    elif "V" in name:
        return "(m/s)"
    elif name[0:2] == "dM":
        return "Mass Flow Rate (kg/s)"
    elif name[0:2].lower() == "dp":
        return "Pressure (psi)"
    elif unit == "M":
        return "Mass (kg)"
    elif unit == "T" or "ISP" in name:
        return "(s)"
    return ""

def get_actuation_indexes(values: list) -> list:
    '''Returns a list of all the indexes at which an actuator swtiches from on to of or vice versa'''
    res = []
    for i in range(len(values) - 1):
        if values[i] > values[i+1]:
            res.append((i, "Off"))
        elif values[i] < values[i+1]:
            res.append((i, "On"))
    return res

def get_available_folders() -> list:
    cur_dir = os.path.join(os.getcwd(), "CarinaLogProcessorPlotter")
    if not os.path.exists(os.path.join(cur_dir, "Data")):
        os.makedirs(os.path.join(cur_dir, "Data"))

    available_folders = []
    dir_items = os.scandir(os.path.join(cur_dir, "Data"))
    for item in dir_items:
        if item.is_dir():
            if os.path.exists(os.path.join(cur_dir, "Data", item, "raw", "data.log")) and os.path.exists(os.path.join(cur_dir, "Data", item, "raw", "events.log")):
                available_folders.append(item.name)
                append_to_log(f"Found valid folder {item.name} at path {os.path.join(cur_dir, 'Data', item)}")
    if not available_folders:
        gui_error("No valid data folders found! Please add a data.log and events.log file to a testfolder in a /raw subdirectory. Note all test folders must go in the /Data folder.")
        append_to_log("Failed to find any valid data folders", "ERROR")
        available_folders = [""]
    return available_folders
            
def append_to_log(msg: str, mode: str = 'INFO') -> None:
    '''Function to append a message to the program.log file based on th emessage and message type (mode). '''
    try:
        with open("program.log", "a") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], {mode}: {msg}\n')
            file.close()
    except Exception as e:
        gui_error(f"Error adding to program log. Due to {e}")


