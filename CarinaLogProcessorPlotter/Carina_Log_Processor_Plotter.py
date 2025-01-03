from _thread import *
from customtkinter import *
from queue import Queue
from datetime import datetime
from CarinaLogProcessorPlotter.src.carina_parser import parser 
from CarinaLogProcessorPlotter.src.GUItools import *

import pandas as pd

class CarinaLogProcessorPlotter(CTk):
    def __init__(self, Title: str) -> None:
        super().__init__() # Initializes Window object of Tkinter
        self.queue = Queue() # Queue for use in multiprocessing
        # The next object variables for proccessing functions which numerically integrate and differenciate
        self.diff_hs_size = 900
        self.int_type = "Simpson"
        self.int_step_size = 100
        # Create new program log and append first entry
        with open("program.log", "w") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], INFO: Program Started\n')
            file.close()
        # Sets visual mode to dark as default and to blue
        set_appearance_mode("dark") 
        set_default_color_theme("blue") 
        self.title(Title) # Title of aplication which is provided when initializing object
        self.boot_screen() # call first screen 
        self.mainloop() # runs tkinter loop
        
    def boot_screen(self) -> None: # First screen user sees and allows them to choose the folder
        # Clears screen and set data variables to nothing this is to clear ram if user has pressed back button
        tools.clear_gui(self)
        self.actuator_df = None
        self.sensor_df = None
        # Sets up all the screen elements
        boot_frm = CTkFrame(master=self)
        greeting_lbl = CTkLabel(master=boot_frm, text="Welcome to the Carina Data Plotter", text_color="lightblue", font=("Arial", 30))
        prompt_frm = CTkFrame(master=boot_frm)
        prompt_frm.rowconfigure((0, 1, 2), weight=2)
        prompt_frm.columnconfigure((0, 1, 2), weight=1)
        prompt_lbl = CTkLabel(master=prompt_frm, text='Choose test folder which you want to analyze: ', font=("Arial", 16), anchor="center")
        folder_opt = CTkOptionMenu(master=prompt_frm, font=("Arial", 12), values=tools.get_available_folders())
        immediatetly_plot_frm = CTkFrame(master=prompt_frm)
        immediatetly_plot_frm.rowconfigure((0), weight=1)
        immediatetly_plot_frm.columnconfigure((0, 1, 2), weight=1)
        immediatetly_plot_label =  CTkLabel(master=immediatetly_plot_frm, font=("Arial", 16), text="Immediatetly Plot:", anchor="center")
        plot = IntVar(value=0)
        plot_rdbtn = CTkRadioButton(master=immediatetly_plot_frm, text="Yes", font=("Arial", 12), value=1, variable=plot)
        noplot_rdbtn = CTkRadioButton(master=immediatetly_plot_frm, text="No", font=("Arial", 12), value=0, variable=plot)
        save_frm = CTkFrame(master=prompt_frm)
        save_frm.rowconfigure((0), weight=1)
        save_frm.columnconfigure((0, 1, 2), weight=1)
        save_lbl = CTkLabel(master=save_frm, font=("Arial", 16), text="Save Plots:", anchor="center")
        save = IntVar(value=0)
        save_rdbtn = CTkRadioButton(master=save_frm, text="Yes", font=("Arial", 12), value=1, variable=save)
        nosave_rdbtn = CTkRadioButton(master=save_frm, text="No", font=("Arial", 12), value=0, variable=save)
        start_program_btn = CTkButton(master=boot_frm, text="Start Program", font=("Arial", 20), width=120, anchor="center", command=tools.textbox_caller(self.loading_screen, folder_opt, plot, save))
        
        greeting_lbl.pack(pady=20)
        prompt_lbl.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(10, 5), sticky="nsew")
        folder_opt.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        immediatetly_plot_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        plot_rdbtn.grid(row=0, column=1, padx=(30, 0), pady=(10, 10), sticky="nsew")
        noplot_rdbtn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        immediatetly_plot_frm.grid(row=2, column=0, columnspan=3, pady=10, padx=10)
        save_lbl.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        save_rdbtn.grid(row=0, column=1, padx=(30, 0), pady=(10, 10), sticky="nsew")
        nosave_rdbtn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        save_frm.grid(row=3, column=0, columnspan=3, pady=10, padx=10)
        prompt_frm.pack(padx=5, expand=True)
        start_program_btn.pack(pady=20)
        boot_frm.pack(pady=20, padx=30, fill="both", expand=True)

    def loading_screen(self, folder_name: str, plot: int, save: int) -> None: # Loading window which pops up when users start program and while program processes data
        # Clears screen
        tools.clear_gui(self)
        # Sets up window visuals
        self.folder_name = folder_name
        messages = ["Initalizing Parser", "Reading data.log", "Reading events.log", "Parsing Sensor Lines", "Parsing Actuator Lines", "Reformating Actuators Data and Converting to Dataframes", "Creating Graphs", "Complete"]
        loading_frm = CTkFrame(master=self)
        loading_lbl = CTkLabel(master=loading_frm, text="Loading...", font=("Arial", 25))
        progress_bar = CTkProgressBar(master=loading_frm, orientation="horizontal", width = 190, height = 25)
        progress_bar.set(0)
        info_lbl = CTkLabel(master=loading_frm, text=messages[0], font=("Arial", 14))
        loading_lbl.pack(pady=15)
        progress_bar.pack(padx = 30,)
        info_lbl.pack(pady=5, padx=5)
        loading_frm.pack(padx=20, pady=30)
        self.update()
        # starts thread so visuals can still update while the program proccesses the data in the backgrounf
        start_new_thread(self.data_processor, (folder_name, ))
        # loop to update progress bar
        progress = 0
        while progress < 0.85:
            val = self.queue.get()
            progress = val/7
            progress_bar.set(progress)
            info_lbl.configure(text=messages[val])
            tools.append_to_log(messages[val], "INFO")
            self.update()
        progress_bar.set(1)
        info_lbl.configure(text=messages[7])
        self.update()
        # Once data processing done, plot all if plotting was chosen and add to log
        if plot == 1:
            self.plot_all(save=save)
        tools.append_to_log(f"Data Parsing and Plotting Complete", "INFO")
        self.data_screen() # go to main tool screen

    def data_processor(self, folder_name: str) -> None: # This function handles processing the carina logs 
        # constantly pushes number to queue so the threaded funcitons can communicate and so the progres sbar can be updated
        self.queue.put(0)
        parser.init(folder_name) # intializes globals in parser file
        self.queue.put(1)
        # gets sensor and actuator lists using parser function
        sensors, actuators = parser.parse_from_raw(self.queue)
        self.queue.put(5)
        # converts sensor and actuator lists to pandas dataframe
        self.sensor_df, self.actuator_df = parser.dataframe_format(sensors, actuators)
        self.queue.put(6)
        return # breaks out of thread
    
    def plot_all(self, start_time = 0, end_time = None, save: int = 0) -> None: # Responsible for plotting all the actuators and sensors in the datarframes, then logs it 
        tools.generate_plots(self.folder_name, self.sensor_df, "sensor", start_time, end_time, save)
        tools.generate_plots(self.folder_name, self.actuator_df, "actuator", start_time, end_time, save)
        tools.append_to_log(f'Generated {len(self.sensor_df.columns) + len(self.actuator_df.columns) - 2} Plots', "INFO")

    def custom_plot(self, options: list[list, list, list], start = 0, end = None, save:int = 0, plot_name = None): # Used to create a singular cusotmized plot, and logs it
        # Gets time xaxis and the start and end indexes
        time = self.sensor_df["Time"].tolist() 
        start = tools.get_xaxis_index(time, start)
        end = tools.get_xaxis_index(time, end) + 1
        # gets the y_data for the left an right axis and using sensor name and also get's masss flow rate if that is what was requested
        left_axis = []
        for sensor in options[0]: 
            if sensor[0:2] == "dM":
                mass_flow = processors.mass_flow_rate(sensor, self.sensor_df, start, end) # Makes call to processor file to get mas flow rate
                left_axis.append((sensor, mass_flow))
            else:
                left_axis.append((sensor, self.sensor_df[sensor].tolist()[start:end])) 
        right_axis = []
        for sensor in options[1]:
            if sensor[0:2] == "dM":
                mass_flow = processors.mass_flow_rate(sensor, self.sensor_df, start, end)
                right_axis.append((sensor, mass_flow))
            else:
                right_axis.append((sensor, self.sensor_df[sensor].tolist()[start:end]))
        # gets actuators y_data from dataframe using the actuator name 
        actuators = []
        for actuator in options[2]:
            actuators.append((actuator, self.actuator_df[actuator].tolist()[start:end]))
        time = time[start:end]
        # makes plot by calling single plot function
        tools.single_plot(self.folder_name, time, left_axis, right_axis, actuators, save, plot_name)
        tools.append_to_log("Created a new custom plot", "INFO:")     

    def custom_save(self, options: list[list, list, list], start = 0, end = None, filename = None):
        time = self.sensor_df["Time"].tolist() 
        start = tools.get_xaxis_index(time, start)
        end = tools.get_xaxis_index(time, end) + 1

        sensors = options[0] + options[1]
        actuators = options[2]
        if sensors == [] and actuators == []:
            tools.gui_popup("No Sensors or Actuators were selected. No data was saved.")
            return

        d = {"Time": time[start:end]}
        for sensor in sensors:
            if sensor[0:2] == "dM":
                mass_flow = processors.mass_flow_rate(sensor, self.sensor_df, start, end) # Makes call to processor file to get mas flow rate
                d[sensor] = mass_flow
            else:
               d[sensor] = self.sensor_df[sensor].tolist()[start:end]
        for actuator in actuators:
            d[actuator] = self.actuator_df[actuator].tolist()[start:end]

        df = pd.DataFrame(d)
        df.to_csv(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", self.folder_name, "Plots", f"{filename}.csv"))
        tools.append_to_log(f"Saved custom data to CSV titles '{filename}.csv' ", "INFO:")   
            
    def data_screen(self) -> None: # Creates the main tool screen
        # Clears screen and set processor file global variables
        tools.clear_gui(self)
        processors.set_parameters(self.diff_hs_size, self.int_type, self.int_step_size)

        # Makes grid for page and sets title
        self.grid_columnconfigure((0, 1, 2, 4), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        title_frm = CTkFrame(master=self)
        title_frm.grid_columnconfigure((0, 1), weight=1)
        title_lbl = CTkLabel(master=title_frm, text="Data Processor & Plotter", text_color="lightblue", font=("Arial", 30))
        title_lbl.grid(row = 0, column = 0, pady=30, columnspan=2, sticky="ew")
        title_frm.grid(row = 0, column = 0, padx=10, pady=5, columnspan=4, sticky="nsew")
  
        # creates visuals for replot all tool
        replot_frm = CTkFrame(master=self)
        replot_frm.grid_columnconfigure((0, 1), weight=1)
        replot_frm.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        replot_lbl = CTkLabel(master=replot_frm, text="Replot All", font=("Arial", 22))
        replot_lbl.grid(row = 0, column = 0, padx=10, pady=10, columnspan=2, sticky="ew")
        start_time_lbl = CTkLabel(master=replot_frm, text="Start Time:", font=("Arial", 14))
        start_time_lbl.grid(row=1, column=0, pady=10, padx=(10, 0), sticky="ew")
        start_time_ent = CTkEntry(master=replot_frm, font=("Arial", 14), width=80)
        start_time_ent.grid(row=1, column=1, pady=10, padx=(0, 10))
        end_time_lbl = CTkLabel(master=replot_frm, text="End Time:", font=("Arial", 14))
        end_time_lbl.grid(row=2, column=0, pady=10, padx=(10, 0), sticky="ew")
        end_time_ent = CTkEntry(master=replot_frm, font=("Arial", 14), width=80)
        end_time_ent.grid(row=2, column=1, pady=10, padx=(0, 10))
        save_frm = CTkFrame(master=replot_frm)
        save_frm.rowconfigure((0), weight=1)
        save_frm.columnconfigure((0, 1, 2), weight=1)
        save_lbl = CTkLabel(master=save_frm, font=("Arial", 16), text="Save Plots:", anchor="center")
        save = IntVar(value=0)
        save_rdbtn = CTkRadioButton(master=save_frm, text="Yes", font=("Arial", 12), value=1, variable=save)
        nosave_rdbtn = CTkRadioButton(master=save_frm, text="No", font=("Arial", 12), value=0, variable=save)
        save_lbl.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        save_rdbtn.grid(row=0, column=1, padx=(30, 0), pady=(10, 10), sticky="nsew")
        nosave_rdbtn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        save_frm.grid(row=3, column=0, columnspan=2, pady=10, padx=10)
        replot_btn = CTkButton(master=replot_frm, text="Replot", width=140, font=("Arial", 18), anchor="center", command=tools.replot_caller(self.plot_all, start_time_ent, end_time_ent, save))
        replot_btn.grid(row=5, column=0, columnspan=2, pady=20, padx=10)
        replot_frm.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), rowspan=2, sticky="nsew")
        
        # Sets up visuals for cusotm plot tool
        self.get_sensor_options() # Gets options for sensors based on dataframe
        custom_plot_frm = CTkFrame(master=self)
        custom_plot_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        custom_plot_frm.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        cutom_plot_lbl = CTkLabel(master=custom_plot_frm, text="Create Custom Plot", font=("Arial", 22))
        cutom_plot_lbl.grid(row = 0, column = 0, padx=10, pady=10, columnspan=4, sticky="ew")
        custom_title_lbl = CTkLabel(master=custom_plot_frm, text="Plot Name (optional): ", font=("Arial", 16))
        custom_title_lbl.grid(row=1, column=0, padx=(10, 0), pady=10, sticky="ew")
        custom_title_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=100)
        custom_title_ent.grid(row=1, column=1, columnspan=3, padx=(0, 10), pady=10, sticky="ew")
        start_lbl = CTkLabel(master=custom_plot_frm, text="Start Time:", font=("Arial", 16))
        start_lbl.grid(row=3, column=0, pady=10, padx=(10, 0), sticky="ew")
        start_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=200)
        start_ent.grid(row=3, column=1, pady=10, padx=(0, 5), sticky = "w")
        end_lbl = CTkLabel(master=custom_plot_frm, text="End Time:", font=("Arial", 16))
        end_lbl.grid(row=3, column=2, pady=10, padx=(5, 0), sticky="w")
        end_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=200)
        end_ent.grid(row=3, column=3, pady=10, padx=(0, 10), sticky = "w")
        actuator_frame = guiClasses.ActuatorTimeDropdown(master=custom_plot_frm, actuator_df=self.actuator_df, entry_boxes=[start_ent, end_ent], text="Actuator Timelines: ")
        actuator_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        choices_frm = CTkFrame(master=custom_plot_frm)
        choices_frm.grid_rowconfigure((0, 1), weight=1)
        choices_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        independent_lbl = CTkLabel(master=choices_frm, text="Independent", font=("Arial", 16))
        actuator_lbl = CTkLabel(master=choices_frm, text="Actuators", font=("Arial", 16))
        independent_opt = CTkOptionMenu(master=choices_frm, font=("Arial", 14), values=["Time"], anchor="center")
        left_axis_lbl = CTkLabel(master=choices_frm, text="Left Axis", font=("Arial", 14))
        right_axis_lbl = CTkLabel(master=choices_frm, text="Right Axis", font=("Arial", 14))
        self.left_axis_options = guiClasses.OptionsColumn(master=choices_frm, values=self.sensor_options)
        self.right_axis_options = guiClasses.OptionsColumn(master=choices_frm, values=self.sensor_options)
        actuators_options = guiClasses.OptionsColumn(master=choices_frm, values=self.actuator_df.columns.to_list()[1:], ctype="A")
        independent_lbl.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="ew")
        actuator_lbl.grid(row=0, column=3, padx=(10, 0), pady=10, sticky="ew")
        independent_opt.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        left_axis_lbl.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        right_axis_lbl.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="ew")
        self.left_axis_options.grid(row=1, column=1, padx=10, pady=10, sticky ="nsew")
        self.right_axis_options.grid(row=1, column=2, padx=10, pady=10, sticky ="nsew")
        actuators_options.grid(row=1, column=3, rowspan=2, padx=10, pady=10, sticky ="nsew")
        choices_frm.grid(row=4, column=0, columnspan=4, padx = 10, pady=10, stick="nsew")
        save2_frm = CTkFrame(master=custom_plot_frm)
        save2_frm.grid_rowconfigure((0), weight=1)
        save2_frm.grid_columnconfigure((0, 1, 2), weight=1)
        save2_lbl = CTkLabel(master=save2_frm, font=("Arial", 16), text="Save Plot:", anchor="center")
        save2 = IntVar(value=0)
        save2_rdbtn = CTkRadioButton(master=save2_frm, text="Yes", font=("Arial", 12), value=1, variable=save2)
        nosave2_rdbtn = CTkRadioButton(master=save2_frm, text="No", font=("Arial", 12), value=0, variable=save2)
        save2_lbl.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        save2_rdbtn.grid(row=0, column=1, padx=(30, 0), pady=(10, 10), sticky="nsew")
        nosave2_rdbtn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        save2_frm.grid(row=5, column=0, columnspan=4, pady=10, padx=10)
        custom_plot_btn = CTkButton(master=custom_plot_frm, text="Create Plot", font=("Arial", 18), command=tools.custom_plot_caller(self.custom_plot, (start_ent, end_ent), (self.left_axis_options, self.right_axis_options, actuators_options), save2, custom_title_ent)) # change command
        custom_plot_btn.grid(row=6, column=0, columnspan=2, padx=(60, 10), pady=(10, 10), sticky="ew")
        save_data_btn = CTkButton(master=custom_plot_frm, text="Save Data", font=("Arial", 18), command=tools.custom_save_caller(self.custom_save, (start_ent, end_ent), (self.left_axis_options, self.right_axis_options, actuators_options), custom_title_ent))
        save_data_btn.grid(row=6, column=2, columnspan=2, padx=(10, 60), pady=(10, 10), sticky="ew")
        custom_plot_frm.grid(row=1, column=1, padx=5, pady=(5, 10), rowspan=5, columnspan=2, sticky="nsew")

        # Sets up engine calculations tool visuals
        engine_calc_frm = CTkFrame(master=self)
        engine_calc_frm.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        engine_calc_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        engine_lbl = CTkLabel(master=engine_calc_frm, text="Engine Calculations", font=("Arial", 22))
        engine_lbl.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        wmass_lbl = CTkLabel(master=engine_calc_frm, text="Wet Mass (kg): ", font=("Arial", 14))
        wmass_lbl.grid(row=1, column=0, pady=10, padx=(10, 0), sticky="ew")
        wmass_ent = CTkEntry(master=engine_calc_frm, font=("Arial", 14), width=50)
        wmass_ent.grid(row=1, column=1, pady=10, padx=(0, 10), sticky="ew")
        dmass_lbl = CTkLabel(master=engine_calc_frm, text="Dry Mass (kg): ", font=("Arial", 14))
        dmass_lbl.grid(row=1, column=2, pady=10, padx=(10, 0), sticky="ew")
        dmass_ent = CTkEntry(master=engine_calc_frm, font=("Arial", 14), width=50)
        dmass_ent.grid(row=1, column=3, pady=10, padx=(0, 10), sticky="ew")
        start2_lbl = CTkLabel(master=engine_calc_frm, text="Start Time:", font=("Arial", 16))
        start2_lbl.grid(row=2, column=0, pady=10, padx=(10, 0), sticky="ew")
        start2_ent = CTkEntry(master=engine_calc_frm, font=("Arial", 16), width=60)
        start2_ent.grid(row=2, column=1, pady=10, padx=(0, 10), sticky="ew")
        end2_lbl = CTkLabel(master=engine_calc_frm, text="End Time:", font=("Arial", 16))
        end2_lbl.grid(row=2, column=2, pady=10, padx=(10, 0), sticky="ew")
        end2_ent = CTkEntry(master=engine_calc_frm, font=("Arial", 16), width=60)
        end2_ent.grid(row=2, column=3, pady=10, padx=(0, 10), sticky="ew")
        save3_frm = CTkFrame(master=engine_calc_frm)
        save3_frm.grid_rowconfigure((0), weight=1)
        save3_frm.grid_columnconfigure((0, 1, 2), weight=1)
        save3_lbl = CTkLabel(master=save3_frm, font=("Arial", 16), text="Save Plots:", anchor="center")
        save3 = IntVar(value=0)
        save3_rdbtn = CTkRadioButton(master=save3_frm, text="Yes", font=("Arial", 12), value=1, variable=save3)
        nosave3_rdbtn = CTkRadioButton(master=save3_frm, text="No", font=("Arial", 12), value=0, variable=save3)
        save3_lbl.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        save3_rdbtn.grid(row=0, column=1, padx=(30, 0), pady=(10, 10), sticky="nsew")
        nosave3_rdbtn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        save3_frm.grid(row=3, column=0, columnspan=4, pady=10, padx=10)
        results_lbl = CTkLabel(master=engine_calc_frm, text="Results", font=("Arial", 18))
        results_lbl.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        results_txt = CTkTextbox(master=engine_calc_frm, font=("Arial", 16), state="disabled")
        results_txt.grid(row=6, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")
        run_btn = CTkButton(master=engine_calc_frm, text="Run", font=("Arial", 16), command=tools.engine_calc_caller(self.engine_calculations, (start2_ent, end2_ent), (wmass_ent, dmass_ent), save3, results_txt))
        run_btn.grid(row=4, column=1, columnspan=2, padx=(5,15), pady=10, sticky="ew")
        engine_calc_frm.grid(row=1, column=3, rowspan=3, padx=(5, 10), pady=(5, 10), sticky="nsew")

        # Sets up the visuals for the custom dataset creation tool
        custom_dataset_frm = CTkFrame(master=self)
        custom_dataset_frm.grid_columnconfigure((0, 1, 2), weight=1)
        custom_dataset_frm.grid_rowconfigure((0, 1, 2, 3), weight=1)
        dataset_lbl = CTkLabel(master=custom_dataset_frm, text="Make Custom Dataset", font=("Arial", 22))
        dataset_lbl.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        dataset_name_lbl = CTkLabel(master=custom_dataset_frm, text="New Dataset Name: ", font=("Arial", 16))
        dataset_name_lbl.grid(row=1, column=0, padx=(10, 0), pady=10, sticky="ew")
        dataset_name_ent = CTkEntry(master=custom_dataset_frm, font=("Arial", 16), width=150)
        dataset_name_ent.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=10, sticky="w")
        operation = guiClasses.OperationSelector(master=custom_dataset_frm, sensor_df=self.sensor_df)
        operation.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        create_buttom = CTkButton(master=custom_dataset_frm, text="Create Dataset", font=("Arial", 16), width=200, height=40, command=tools.custom_dataset_caller(self.custom_dataset, operation, dataset_name_ent))
        create_buttom.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        custom_dataset_frm.grid(row=4, column=3, rowspan=2, padx=(5, 10), pady=(5, 10), sticky="nsew")

        # Sets up visuals for the export parsed data tool
        export_frm = CTkFrame(master=self)
        export_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        export_frm.grid_rowconfigure((0, 1, 2), weight=1)
        export_lbl = CTkLabel(master=export_frm, text="Export Parsed Data to CSV", font=("Arial", 22))
        export_lbl.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        export_start_lbl = CTkLabel(master=export_frm, text="Start Time:", font=("Arial", 16))
        export_start_ent = CTkEntry(master=export_frm, font=("Arial", 16), width=50)
        export_end_lbl = CTkLabel(master=export_frm, text="End Time:", font=("Arial", 16))
        export_end_ent = CTkEntry(master=export_frm, font=("Arial", 16), width=50) 
        export_btn = CTkButton(master=export_frm, text="Export Data", font=("Arial", 16), command=lambda: self.export_data(export_start_ent.get(), export_end_ent.get()))
        export_start_lbl.grid(row=1, column=0, padx=(10, 1), pady=10, sticky="ew")
        export_start_ent.grid(row=1, column=1, padx=(1, 5), pady=10, sticky="ew")
        export_end_lbl.grid(row=1, column=2, padx=(5, 1), pady=10, sticky="ew")
        export_end_ent.grid(row=1, column=3, padx=(1, 10), pady=10, sticky="ew")
        export_btn.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        export_frm.grid(row=3, column=0, rowspan=2, padx=(10, 5), pady=(5, 10), sticky="nsew")

        # Sets up visuals for the return to main menu buttons and the log and settings buttons to bring users to new windows. 
        buttons_frm = CTkFrame(master=self)
        buttons_frm.grid_rowconfigure((0, 1), weight=1)
        buttons_frm.grid_columnconfigure((0, 1), weight=1)
        back_btn = CTkButton(master=buttons_frm, text="Return to Menu", font=("Arial", 16), anchor="center", height=50, width=180, command=self.boot_screen)
        back_btn.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=10)
        log_btn = CTkButton(master=buttons_frm, text="Logs", font=("Arial", 16), anchor="center", height=35, command=self.logs_screen)
        log_btn.grid(row=0, column=0, pady=(20, 0), padx=(10, 7))
        configuration_btn = CTkButton(master=buttons_frm, text="Settings", font=("Arial", 16), anchor="center", height=35, command=self.configuration_screen) # Change this
        configuration_btn.grid(row=0, column=1, pady=(20, 0), padx=(7, 10))
        buttons_frm.grid(row=5, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew")
        
    def configuration_screen(self)->None: # Settings window for user to edit the program settings
        # Creates new window and set's title
        window = CTkToplevel()
        window.title("Settings")

        # Sets up grid for the window
        window.grid_columnconfigure((0, 1), weight=1)
        window.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        # Sets up the visuals for the window 
        configurations_lbl = CTkLabel(master=window, text="Settings", font=("Arial", 22))
        configurations_lbl.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")
        diff_step_size_lbl = CTkLabel(master=window, text="Differenciation Half Step Size:", font=("Arial", 16))
        diff_step_size_ent = CTkEntry(master=window, width = 50, font=("Arial", 16), placeholder_text=self.diff_hs_size)
        int_step_size_lbl = CTkLabel(master=window, text="Integration Step Size:", font=("Arial", 16))
        int_step_size_ent = CTkEntry(master=window, width = 50, font=("Arial", 16), placeholder_text=self.int_step_size)
        int_type_lbl = CTkLabel(master=window, text="Integration Method:", font=("Arial", 16))
        int_type_opt = CTkOptionMenu(master=window, values=["Trapezoid", "Simpson"], font=("Arial", 16))
        int_type_opt.set(self.int_type)
        visual_switch = CTkSwitch(master=window, text="Visual Mode", command=self.switch_visual_mode)
        visual_switch.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="")
        diff_step_size_lbl.grid(row=1, column=0, padx=(10, 2), pady=10, sticky="ew")
        diff_step_size_ent.grid(row=1, column=1, padx=(2, 10), pady=10, sticky="ew")
        int_type_lbl.grid(row=2, column=0, padx=(10, 2), pady=10, sticky="ew")
        int_type_opt.grid(row=2, column=1, padx=(2, 10), pady=10, sticky="ew")
        int_step_size_lbl.grid(row=3, column=0, padx=(10, 2), pady=10, sticky="ew")
        int_step_size_ent.grid(row=3, column=1, padx=(2, 10), pady=10, sticky="ew")
        save_btn = CTkButton(master=window, text="Save Changes", font=("Arial", 16), anchor="center", command=lambda: self.config(diff_step_size_ent.get(), int_type_opt.get(), int_step_size_ent.get()))
        save_btn.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def logs_screen(self)->None: # Sets up logs window which shows program log
        # Sets up window and gives it a title
        window = CTkToplevel()
        window.title("Program Logs")
        # Creates visuals for the logs window
        logs_lbl = CTkLabel(master=window, text="Program Log", font=("Arial", 20))
        logs_lbl.grid(row=0, column=0, columnspan=3, padx=10, pady=(20, 10), sticky="nsew")
        logs_txt = CTkTextbox(master=window, font=("Arial", 16), width=700)
        logs_txt.grid(row=1, column=0, columnspan=3, rowspan=5, padx=10, pady=10, sticky="nsew")
        #Loop inserts each line from the program.log file into the text box.
        with open("program.log", "r") as file:
            for line in file:
                logs_txt.insert("end", line)
        logs_txt.configure(state="disabled")
        logs_txt.see("end") #scrolls to the bottom fo the text box

    def config(self, diff_step_size: int, int_method: str, int_step_side: int)->None: # Function called by the save settings button in the settings page
        # use try and excpet to handle invalid input
        try:
            # Re sets program variables
            self.diff_hs_size = int(diff_step_size)
            self.int_type = int_method
            self.int_step_size = int_step_side
            # Sets the new values to the variables in the proccessor file 
            processors.set_parameters(self.diff_hs_size, self.int_type, self.int_step_size)
            tools.gui_popup("Succesfully Applied New Configuration!") # Provides succesful message and logs it 
            tools.append_to_log(f"Changed Differention Half Step Size to {diff_step_size}, changed integration method to {self.int_type}, changed integration step size to {self.int_step_size}")
        except Exception as e:
            # Provides pop up error and logs error
            tools.gui_error("CONFIGURATION ERROR: Invalid Input")
            tools.append_to_log(f"Failed to change configurations due to {e}", "ERROR")

    def get_sensor_options(self)->None: # Gets options that can be sekected for plotting
        self.sensor_options = self.sensor_df.columns.to_list()[1:]
        # Chekcs for the possibility of mass flow rate being an option if mass of tanks exists
        if "MFT" in self.sensor_options:
            self.sensor_options.append("dMFT")
        if "MOT" in self.sensor_options:
            self.sensor_options.append("dMOT")

    def engine_calculations(self, text_box: CTkTextbox, wet_masss: float, dry_masss: float, start_time: float, end_time = None, save:int = 0)->None: # Called by engine calculations tool and Fascilatates all the engine calculations and plotting and displaying results
        # Gets x_axis/time, start anf end index
        time = self.sensor_df["Time"].to_list()
        start_ind = tools.get_xaxis_index(time, start_time)
        if end_time is None:
            end_ind = len(time) - 1
        else:
            end_ind = tools.get_xaxis_index(time, end_time)
        # checks to ensure we have nescscary data needed to perform engine calculations
        if "MFT" in self.sensor_df.columns and "MOT" in self.sensor_df.columns:
            # gets results from proccessor file
            results = processors.engine_calculations(self.sensor_df, wet_masss, dry_masss, start_ind, end_ind)
            time = time[start_ind:end_ind]
            # Empties/resets text box
            text_box.configure(state="normal")
            text_box.delete(0, 'end')
            # Checks whether item in result is a list or value and then either plots it or puts value in text box
            for res in results:
                if isinstance(res[1], list):
                    tools.single_plot(self.folder_name, time, [res], [], [], save)
                else:
                    text_box.insert("end", f'{res[0]}: {res[1]}{tools.get_units(res[0])}\n')
            text_box.configure(stae='disabled')
            tools.append_to_log("Ran engine calculations") # appends result
        else:
            # Provides error pop up and appends to log
            tools.gui_error("Cannot run engine calculations as you are missing either MFT or MOT or both.")
            tools.append_to_log("Unable to run engine calculations as required sensor data is missing", "ERROR")

    def custom_dataset(self, sensors:list, operator:str, name:str): # Function that is called by cusotm dataset tool anf fascialtates the creation of a new dataset
        # Uses proccessor file to make new dataset form user input
        new_dataset = processors.custom_dataset(sensors[0], sensors[1], self.sensor_df, operator)
        self.sensor_df[name] = new_dataset # adds to dataframe
        #Resets opitons of sensors users can select forr plotting
        self.sensor_options = self.sensor_df.columns.to_list()[1:]
        if "MFT" in self.sensor_options:
            self.sensor_options.append("dMFT")
        if "MOT" in self.sensor_options:
            self.sensor_options.append("dMOT")
        # updates it in objects of dropdown list in cusotm plot tool
        self.left_axis_options.update_values(self.sensor_options)
        self.right_axis_options.update_values(self.sensor_options)
        tools.append_to_log(f"New dataset created called {name}, created by doing {sensors[0]} {operator} {sensors[1]}") # Appends info to log 
        
    def switch_visual_mode(self): #is used to switch visual mode of the application and ads to log
        if get_appearance_mode() == "Dark":
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")
        tools.append_to_log(f"Changed appearance mode to {get_appearance_mode()}", "INFO")

    def export_data(self, start, end)-> None: # function called by export function tool 
        # Uses try and except to deal with user error
        try:
            # validates start and end time and gets their values 
            if start > end:
                tools.gui_error("EXPORT DATA ERROR: Start time cannot be larger then end time.")
                return
            if end == "":
                end = self.sensor_df["Time"][len(self.sensor_df) - 1]
            else:
                end = min(self.sensor_df["Time"][len(self.sensor_df) - 1], float(end))
            if start == "":
                start = self.sensor_df["Time"][0]
            else:
                start = max(self.sensor_df["Time"][0], float(start))
            # makes coppies of dataframe but within the timeframe of start and end
            sensor_df = self.sensor_df[(self.sensor_df["Time"] >= start) & (self.sensor_df["Time"] <= end)]
            actuator_df = self.actuator_df[(self.sensor_df["Time"] >= start) & (self.sensor_df["Time"] <= end)]
            # Gets indexes for start and end
            if end == self.sensor_df["Time"][len(self.sensor_df) - 1]:
                end = tools.get_xaxis_index(self.sensor_df["Time"], end) + 1
            else:
                end = tools.get_xaxis_index(self.sensor_df["Time"], end)
            # add mass flow rate if we have mass values
            if "MFT" in sensor_df.columns:
                sensor_df["dMFT"] = processors.mass_flow_rate("dMFT", self.sensor_df, tools.get_xaxis_index(self.sensor_df["Time"], start), end)
            if "MOT" in sensor_df.columns:
                sensor_df["dMOT"] = processors.mass_flow_rate("dMOT", self.sensor_df, tools.get_xaxis_index(self.sensor_df["Time"], start), end)
            # converts dataframe to csv and saves
            sensor_df.to_csv(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", self.folder_name, "raw", "parsed_sensors_data.csv"))
            actuator_df.to_csv(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", self.folder_name, "raw", "parsed_actuator_data.csv"))
            # provides success pop up and appends to log
            tools.gui_popup(f"Exported Sensors and Actuators Data to CSV in /Data/{self.folder_name}/raw folder")
            tools.append_to_log("Exported Sensors and Actuators Data to CSV in /Data/{self.folder_name}/raw folder")
        except Exception as e:
            # provides failure pop up and appends to log
            tools.gui_error("EXPORT DATA ERROR: Invalid start or end time.")
            tools.append_to_log(f"Fialed to export data to csv due to {e}", "ERROR")
            
