
import os
import pandas as pd
import matplotlib.pyplot as plt
import time as t
from customtkinter import *
from tkinter import messagebox
from datetime import datetime


def textbox_caller(func, text_box: CTkEntry, save: IntVar):
    def call_func():
        text = text_box.get()
        folder = os.path.join(os.getcwd(), "Data", text, "raw")
        if not os.path.exists(os.path.join(folder, "data.log")) or not os.path.exists(os.path.join(folder, "events.log")):
            gui_error("File Path not Found")
            return
        append_to_log(f'Begining data parsing in {folder}', "INFO")
        func(text, save.get())
    return call_func

def replot_caller(func, start_box: CTkEntry, end_box: CTkEntry, save: IntVar):
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
        except Exception:
            gui_error("Invalid Start or End Time")
    return call_func2

def custom_plot_caller(func, times:tuple[CTkEntry, CTkEntry], options:tuple, save: IntVar): 
    def call_func2():
        try:
            choices = (options[0].selections(), options[1].selections(), options[2].selections())
            start = times[0].get()
            end = times[1].get()
            if start == "" and end == "":
                func(choices)
            elif start == "":
                func(choices, end=float(end), save=save.get())
            elif end == "":
                func(choices, start=float(start), save=save.get())
            else:
                if start > end:
                    gui_error("End cannot be less then Start")
                    append_to_log(f"Failed to create graphs as start time was greater then end time (start:{start}, end:{end})", "ERROR")
                    return
                func(choices, float(start), float(end), save.get())
        except Exception:
            gui_error("Invalid Start or End value")
    return call_func2

def add_caller(func, button: CTkButton):
    def call():
        func(button)
    return call

def gui_error(msg: str) -> None:
    messagebox.showerror(title="Program Error", message=msg)
    append_to_log(msg, "ERROR")

def clear_gui(window: CTk) -> None:
    for child in window.children.copy():
        window.children[child].destroy() 
    append_to_log("Clearing GUI Screen", "INFO") 

#add error handeling for colors array, in general improve color handeling fr lines
def single_plot(folder_name: str, time:list, left_axis: list, right_axis:list, actuators:list, save:int = 0) -> None: 
    if not os.path.exists(os.path.join(os.getcwd(), "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(), "Data", folder_name, "Plots"))

    colors = ['b','g','r','c','m','y','k']
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
    plotted = True
    if left_axis and right_axis:
        for sensor in left_axis:
            plt.plot(time, sensor[1], label=sensor[0], color=colors[i])
            i += 1
        plt.ylabel(get_units(sensor[0]))
        ax2 = plt.twinx()
        for sensor in right_axis:
            ax2.plot(time, sensor[1], label=sensor[0], color=colors[i])
            i += 1
        ax2.set_ylabel(get_units(sensor[0]))
    elif left_axis:
        for sensor in left_axis:
            plt.plot(time, sensor[1], label=sensor[0], color=colors[i])
            i += 1
        plt.ylabel(get_units(sensor[0]))
    elif right_axis: 
        for sensor in right_axis:
            plt.plot(time, sensor[1], label=sensor[0], color=colors[i])
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
                plt.plot(new_xaxis, [min(sensor[1]), max(sensor[1])], label=f'{actuator[0]} {actuation[1]}', color=colors[i], linestyle='-.')
                i -= 1
    elif actuators:
        for actuator in actuators:
            plt.plot(time, actuator[1], color=colors[i], label=actuator[0])
            i += 1
        plt.ylabel("On/Off (1 or 0)")

    plt.xlabel("Time (s)")
    plt.title(name)
    fig.legend()
    fig.show()

    if save == 1:
        fig.savefig(os.path.join(os.getcwd(), "Data", folder_name, "Plots", f"{name} vs Time Plot {t.strftime('%Hh%Mm%Ss', t.gmtime(time[0]))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(time[-1]))}.jpg"))

def generate_plots(folder_name: str, dataframe: pd.DataFrame, type: str = "sensor", start_time = 0, end_time = None, save:int = 0) -> None:
    if not os.path.exists(os.path.join(os.getcwd(), "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(),"Data", folder_name, "Plots"))

    time = dataframe["Time"].to_list()
    start = get_xaxis_index(time, start_time)
    end = get_xaxis_index(time, end_time)
    if start == end: start -= 1
    time = time[start:end]
    if type.lower() == "actuator":
        time.append(time[-1] + 0.01)
    for column in dataframe.columns:
        if column != "Time":
            p = plt.figure(column + "vs Time Plot")
            data = dataframe[column].to_list()[start:end]
            if type.lower() == "sensor":
                plt.plot(time, data)
            elif type.lower() == "actuator":
                plt.stairs(data, time)
            plt.title(column + " vs Time Plot")
            plt.xlabel("Time (s)")
            plt.ylabel(column + get_units(column))
            p.show() 
            if save == 1:
                p.savefig(os.path.join(os.getcwd(), "Data", folder_name, "Plots", f"{column} vs Time Plot T[{t.strftime('%Hh%Mm%Ss', t.gmtime(start_time))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(end_time))}].jpg"))

def get_xaxis_index(xaxis: list, given_time) -> int:
    if given_time == 0:
        return given_time
    elif given_time is None:
        return len(xaxis)
    else:
        for i, t in enumerate(xaxis):
            if t > given_time:
                return i - 1
            
def get_units(name: str)->str:
    unit = name[0]
    if unit == "B" or unit == "S" or unit == "E" or "V" in name:
        return "On/Off"
    elif unit == "P":
        return "Pressure (psi)"
    elif name == "MFR":
        return "Mass Flow Rate (kg/s)"
    elif unit == "M":
        return "Mass (kg)"
    elif unit == "T":
        return "(s)"
    
def get_actuation_indexes(values: list) -> list:
    res = []
    for i in range(len(values) - 1):
        if values[i] > values[i+1]:
            res.append((i, "Off"))
        elif values[i] < values[i+1]:
            res.append((i, "On"))
    return res
            
def append_to_log(msg: str, mode: str = 'info') -> None:
    try:
        with open("program.log", "a") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], {mode}: {msg}\n')
            file.close()
    except Exception:
        gui_error("Error adding to program log")


