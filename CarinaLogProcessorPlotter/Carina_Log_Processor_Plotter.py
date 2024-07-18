from _thread import *
from customtkinter import *
from queue import Queue
from datetime import datetime
from src.carina_parser import parser 
from src.GUItools import tools
from src.GUItools import processors
from src.GUItools.guiClasses import OptionsColumn, ActuatorTimeDropdown

class Carina_Log_Processor_Plotter(CTk):
    def __init__(self, Title: str) -> None:
        super().__init__()
        self.queue = Queue()
        self.diff_hs_size = 900
        with open("program.log", "w") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], INFO: Program Started\n')
            file.close()
        set_appearance_mode("dark")
        set_default_color_theme("blue")
        self.title(Title)
        self.boot_screen()
        self.mainloop()
        
    def boot_screen(self) -> None:
        tools.clear_gui(self)
        boot_frm = CTkFrame(master=self)
        greeting_lbl = CTkLabel(master=boot_frm, text="Welcome to the Carina Data Plotter", text_color="lightblue", font=("Arial", 30))
        prompt_frm = CTkFrame(master=boot_frm)
        prompt_frm.rowconfigure((0, 1), weight=2)
        prompt_frm.columnconfigure((0, 1, 2), weight=1)
        prompt_lbl = CTkLabel(master=prompt_frm, text='Enter folder name which contains the data and events logs in a "\\raw" sub folder (Data\\_____\\raw):  ', font=("Arial", 16), anchor="center")
        folder_ent = CTkEntry(master=prompt_frm, font=("Arial", 12), width=100)
        save_frm = CTkFrame(master=prompt_frm)
        save_frm.rowconfigure((0), weight=1)
        save_frm.columnconfigure((0, 1, 2), weight=1)
        save_lbl = CTkLabel(master=save_frm, font=("Arial", 16), text="Save Plots:", anchor="center")
        save = IntVar(value=0)
        save_rdbtn = CTkRadioButton(master=save_frm, text="Yes", font=("Arial", 12), value=1, variable=save)
        nosave_rdbtn = CTkRadioButton(master=save_frm, text="No", font=("Arial", 12), value=0, variable=save)
        start_program_btn = CTkButton(master=boot_frm, text="Start Program", font=("Arial", 20), width=120, anchor="center", command=tools.textbox_caller(self.loading_screen, folder_ent, save))
        greeting_lbl.pack(pady=20)
        prompt_lbl.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(10, 5), sticky="nsew")
        folder_ent.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        save_lbl.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        save_rdbtn.grid(row=0, column=1, padx=(30, 0), pady=(10, 10), sticky="nsew")
        nosave_rdbtn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")
        save_frm.grid(row=2, column=0, columnspan=3, pady=10, padx=10)
        prompt_frm.pack(padx=5, expand=True)
        start_program_btn.pack(pady=20)
        boot_frm.pack(pady=20, padx=30, fill="both", expand=True)

    def loading_screen(self, folder_name: str, save: int) -> None:
        tools.clear_gui(self)
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
        start_new_thread(self.data_processor, (folder_name, ))
        progress = 0
        while progress < 0.85:
            val = self.queue.get()
            progress = val/7
            progress_bar.set(progress)
            info_lbl.configure(text=messages[val])
            tools.append_to_log(messages[val], "INFO")
            self.update()
        self.plot_all(save=save)
        progress_bar.set(1)
        info_lbl.configure(text=messages[7])
        self.update()
        tools.append_to_log(f"Data Parsing and Plotting Complete", "INFO")
        self.data_screen()

    def data_processor(self, folder_name: str) -> None:
        self.queue.put(0)
        parser.init(folder_name)
        self.queue.put(1)
        sensors, actuators = parser.parse_from_raw(self.queue)
        self.queue.put(5)
        self.sensor_df, self.actuator_df = parser.dataframe_format(sensors, actuators)
        self.queue.put(6)
        return
    
    def plot_all(self, start_time = 0, end_time = None, save: int = 0) -> None:
        tools.generate_plots(self.folder_name, self.sensor_df, "sensor", start_time, end_time, save)
        tools.generate_plots(self.folder_name, self.actuator_df, "actuator", start_time, end_time, save)
        tools.append_to_log(f'Generated {len(self.sensor_df.columns) + len(self.actuator_df.columns) - 2} Plots', "INFO")

    def custom_plot(self, options: list[list, list, list], start = 0, end = None, save:int = 0):
        time = self.sensor_df["Time"].tolist()
        start = tools.get_xaxis_index(time, start)
        end = tools.get_xaxis_index(time, end)
        left_axis = []
        for sensor in options[0]: 
            if sensor[0] == "d":
                mass_flow = processors.mass_flow_rate(sensor, self.sensor_df, start, end)
                left_axis.append((sensor, mass_flow))
            else:
                left_axis.append((sensor, self.sensor_df[sensor].tolist()[start:end])) 
        right_axis = []
        for sensor in options[1]:
            if sensor[0] == "d":
                mass_flow = processors.mass_flow_rate(sensor, self.sensor_df, start, end)
                right_axis.append((sensor, mass_flow))
            else:
                right_axis.append((sensor, self.sensor_df[sensor].tolist()[start:end]))
        actuators = []
        for actuator in options[2]:
            actuators.append((actuator, self.actuator_df[actuator].tolist()[start:end]))
        time = time[start:end]
        tools.single_plot(self.folder_name, time, left_axis, right_axis, actuators, save)
        tools.append_to_log("Created a new custom plot", "INFO:")      
            
    def data_screen(self) -> None:
        tools.clear_gui(self)
        processors.set_parameters(self.diff_hs_size)

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        title_frm = CTkFrame(master=self)
        title_frm.grid_columnconfigure((0, 1), weight=1)
        title_lbl = CTkLabel(master=title_frm, text="Data Plot Controller", text_color="lightblue", font=("Arial", 30))
        title_lbl.grid(row = 0, column = 0, pady=30, columnspan=2, sticky="ew")
        title_frm.grid(row = 0, column = 0, padx=10, pady=5, columnspan=4, sticky="nsew")
  
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
        replot_frm.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), rowspan=3, sticky="nsew")

        self.get_sensor_options()
        custom_plot_frm = CTkFrame(master=self)
        custom_plot_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        custom_plot_frm.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        cutom_plot_lbl = CTkLabel(master=custom_plot_frm, text="Create Custom Plot", font=("Arial", 22))
        cutom_plot_lbl.grid(row = 0, column = 0, padx=10, pady=10, columnspan=4, sticky="ew")
        start_lbl = CTkLabel(master=custom_plot_frm, text="Start:", font=("Arial", 16))
        start_lbl.grid(row=2, column=0, pady=10, padx=(10, 0), sticky="ew")
        start_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=60)
        start_ent.grid(row=2, column=1, pady=10, padx=(0, 10), sticky="ew")
        end_lbl = CTkLabel(master=custom_plot_frm, text="End:", font=("Arial", 16))
        end_lbl.grid(row=2, column=2, pady=10, padx=(10, 0), sticky="ew")
        end_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=60)
        end_ent.grid(row=2, column=3, pady=10, padx=(0, 10), sticky="ew")
        actuator_frame = ActuatorTimeDropdown(master=custom_plot_frm, actuator_df=self.actuator_df, entry_boxes=[start_ent, end_ent], text="Actuator Timelines: ")
        actuator_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        choices_frm = CTkFrame(master=custom_plot_frm)
        choices_frm.grid_rowconfigure((0, 1), weight=1)
        choices_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        independent_lbl = CTkLabel(master=choices_frm, text="Independent", font=("Arial", 16))
        actuator_lbl = CTkLabel(master=choices_frm, text="Actuators", font=("Arial", 16))
        independent_opt = CTkOptionMenu(master=choices_frm, font=("Arial", 14), values=["Time"], anchor="center")
        left_axis_lbl = CTkLabel(master=choices_frm, text="Left Axis", font=("Arial", 14))
        right_axis_lbl = CTkLabel(master=choices_frm, text="Right Axis", font=("Arial", 14))
        left_axis_options = OptionsColumn(master=choices_frm, values=self.sensor_options)
        right_axis_options = OptionsColumn(master=choices_frm, values=self.sensor_options)
        actuators_options = OptionsColumn(master=choices_frm, values=self.actuator_df.columns.to_list()[1:], ctype="A")
        independent_lbl.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="ew")
        actuator_lbl.grid(row=0, column=3, padx=(10, 0), pady=10, sticky="ew")
        independent_opt.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        left_axis_lbl.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        right_axis_lbl.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="ew")
        left_axis_options.grid(row=1, column=1, padx=10, pady=10, sticky ="nsew")
        right_axis_options.grid(row=1, column=2, padx=10, pady=10, sticky ="nsew")
        actuators_options.grid(row=1, column=3, rowspan=2, padx=10, pady=10, sticky ="nsew")
        choices_frm.grid(row=3, column=0, columnspan=4, padx = 10, pady=10, stick="nsew")
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
        save2_frm.grid(row=4, column=0, columnspan=4, pady=10, padx=10)
        custom_plot_btn = CTkButton(master=custom_plot_frm, text="Create Plot", font=("Arial", 18), command=tools.custom_plot_caller(self.custom_plot, (start_ent, end_ent), (left_axis_options, right_axis_options, actuators_options), save2)) # change command
        custom_plot_btn.grid(row=5, column=1, columnspan=2, pady=(25, 20), sticky="ew")
        custom_plot_frm.grid(row=1, column=1, padx=5, pady=(5, 10), rowspan=5, columnspan=2, sticky="nsew")

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
        export_frm.grid(row=4, column=0, padx=(5, 10), pady=(5, 10), sticky="nsew")

        buttons_frm = CTkFrame(master=self)
        buttons_frm.grid_rowconfigure((0, 1), weight=1)
        buttons_frm.grid_columnconfigure((0, 1), weight=1)
        back_btn = CTkButton(master=buttons_frm, text="Return", font=("Arial", 16), anchor="center", command=self.boot_screen)
        back_btn.grid(row=1, column=0, columnspan=2, pady=(10, 20), padx=10, sticky="ew")
        log_btn = CTkButton(master=buttons_frm, text="Logs", font=("Arial", 16), anchor="center", command=self.logs_screen)
        log_btn.grid(row=0, column=0, pady=(20, 5), padx=(10, 7), sticky="ew")
        configuration_btn = CTkButton(master=buttons_frm, text="Congfigurations", font=("Arial", 16), anchor="center", command=self.configuration_screen) # Change this
        configuration_btn.grid(row=0, column=1, pady=(20, 5), padx=(7, 10), sticky="ew")
        buttons_frm.grid(row=5, column=0, padx=5, pady=(0, 10), sticky="ew")
        self.update() # why ???
        
    def configuration_screen(self):
        tools.clear_gui(self)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        configurations_lbl = CTkLabel(master=self, text="Configurations", font=("Arial", 22))
        configurations_lbl.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")
        diff_step_size_lbl = CTkLabel(master=self, text="Differenciation Half Step Size:", font=("Arial", 16))
        diff_step_size_ent = CTkEntry(master=self, width = 50, font=("Arial", 16), placeholder_text=self.diff_hs_size)
        visual_switch = CTkSwitch(master=self, text="Visual Mode", command=self.switch_visual_mode)
        visual_switch.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="")
        return_btn = CTkButton(master=self, text="Return", font=("Arial", 16), anchor="center", command=self.data_screen)
        save_btn = CTkButton(master=self, text="Save Changes", font=("Arial", 16), anchor="center", command=lambda: self.config(diff_step_size_ent.get()))
        diff_step_size_lbl.grid(row=1, column=0, padx=(10, 2), pady=10, sticky="ew")
        diff_step_size_ent.grid(row=1, column=1, padx=(2, 10), pady=10, sticky="ew")
        return_btn.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        save_btn.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

    def logs_screen(self):
        tools.clear_gui(self)
        logs_lbl = CTkLabel(master=self, text="Program Log", font=("Arial", 20))
        logs_lbl.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="nsew")
        return_btn = CTkButton(master=self, text="Return", font=("Arial", 18), command=self.data_screen)
        return_btn.grid(row=0, column=2, padx=10, pady=(20, 10))
        logs_txt = CTkTextbox(master=self, font=("Arial", 16), width=700)
        logs_txt.grid(row=1, column=0, columnspan=3, rowspan=5, padx=10, pady=10, sticky="nsew")
        with open("program.log", "r") as file:
            for line in file:
                logs_txt.insert("end", line)
        logs_txt.configure(state="disabled")
        logs_txt.see("end")

    def get_sensor_options(self):
        self.sensor_options = self.sensor_df.columns.to_list()[1:]
        if "MFT" in self.sensor_options:
            self.sensor_options.append("dMFT")
        if "MOT" in self.sensor_options:
            self.sensor_options.append("dMOT")

    def config(self, diff_step_size):
        try:
            self.diff_hs_size = int(diff_step_size)
            processors.set_parameters(self.diff_hs_size)
            tools.gui_popup("Succesfully Applied New Configuration!")
            tools.append_to_log(f"Changed Differention Half Step Size to {diff_step_size}")
        except:
            tools.gui_error("CONFIGURATION ERROR: Invalid Input")

    def switch_visual_mode(self):
        if get_appearance_mode() == "Dark":
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")
        tools.append_to_log(f"Changed appearance mode to {get_appearance_mode()}", "INFO")

    def export_data(self, start, end)-> None:
        try:
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
            sensor_df = self.sensor_df[(self.sensor_df["Time"] >= start) & (self.sensor_df["Time"] <= end)]
            actuator_df = self.actuator_df[(self.sensor_df["Time"] >= start) & (self.sensor_df["Time"] <= end)]
            if end == self.sensor_df["Time"][len(self.sensor_df) - 1]:
                end = tools.get_xaxis_index(self.sensor_df["Time"], end) + 1
            else:
                end = tools.get_xaxis_index(self.sensor_df["Time"], end)
            
            if "MFT" in sensor_df.columns:
                sensor_df["dMFT"] = processors.mass_flow_rate("dMFT", self.sensor_df, tools.get_xaxis_index(self.sensor_df["Time"], start), end)
            if "MOT" in sensor_df.columns:
                sensor_df["dMOT"] = processors.mass_flow_rate("dMOT", self.sensor_df, tools.get_xaxis_index(self.sensor_df["Time"], start), end)
            sensor_df.to_csv(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", self.folder_name, "raw", "parsed_sensors_data.csv"))
            actuator_df.to_csv(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", self.folder_name, "raw", "actuator_sensors_data.csv"))
            tools.gui_popup(f"Exported Sensors and Actuators Data to CSV in /Data/{self.folder_name}/raw folder")
        except:
            tools.gui_error("EXPORT DATA ERROR: Invalid start or end time.")
            