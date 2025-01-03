
# Carina Log Processor and Plotter

## Overview

The Carina Log Processor and Plotter is a GUI-based application designed to read, process, and visualize log data from Carina. The application provides a user-friendly interface for selecting data folders, configuring plot settings, generating plots, exporting parsed data, creating new datasets, and getting engine characteristics from thrust.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/UTATRocketry/Carina-Log-Processor-Plotter.git
   ```
2. Navigate to the project directory:
   ```sh
   cd Carina-Log-Processor-Plotter
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   python main.py
   ```
## Add New Test Data
If you perform a new cold flow, hot fire, or other test you will want to add the Carina log files to the program's Data folder so that you can process it using the program. TO do this follow the below instructions:
1. Create a folder with the name of your test inside of the **Data** folder (New Path: \Carina-Log-Processor-Plotter\CarinaLogProcessorPlotter\Data\\**test_name**)
2. Then add a **raw** subdirectory to your test folder (New Path: \Carina-Log-Processor-Plotter\CarinaLogProcessorPlotter\Data\\**test_name**\raw)
3. Now inside the **raw** subdirectory add the sensors data log file and actuator events log file. These files must have the names **data.log** and **events.log**. Your final new test folder setup should look like this:
- \Carina-Log-Processor-Plotter\CarinaLogProcessorPlotter\Data\\**test_name** 
   - **raw** 
       - **data.log** 
       - **events.log** 
  
## Program Docs

### Start Page 
![image](https://github.com/user-attachments/assets/7def1407-2d02-49e7-bc06-e944bb0ae901)

#### Steps to Start Program
1. Open the application.
2. Choose the folder you want to process from the dropdown menu.
3. Choose whether to save the initial plots or not. (By selecting the radio button)
4. Click the "Start Program" button to process and visualize the data across the entire time domain.
5. After all the initial plots are generated you will find yourself in the main program UI.

### Main Page
![image](https://github.com/user-attachments/assets/f6187df7-6213-4124-a0a4-79f42b8a7fc3)

#### Program Tools
##### Replot All
   This tool allows you to replot all the sensors' and actuators' data just as the program did when you first started it. The main difference is you can also define a time frame to plot between. This is useful if you want to visualize everything during a specific time frame. To use this tool follow the steps below:
1. Click on the "Start Time" entry box and enter the desired start time in seconds. If you want to have it plotted from the beginning you can leave this blank.
2. click on the "End Time" entry box and enter the desired end time in seconds. If you want to plot to the very end you can leave this blank.
3. Next choose whether you want to automatically save all plots when they are generated by clicking on the "Yes" or "No" radio button.
4. Finally click on "Replot" and it will generate the plots.

![image](https://github.com/user-attachments/assets/802e0142-7646-475c-9dc4-4028f7166075)

##### Custom Plot 
   This tool allows you to create singular custom plots of multiple sensors on the same plot and also with actuation times displayed. This allows for better visuals of data and what is truly occurring during testing. To use this tool follow the instructions below:
1. Firstly you can give your plot a custom name by entering your desired title in the "Plot Name (optional):" entry box.
2. Then if you would like to use actuation times to help set the timeframe for your custom graph you can select an actuator from the "Actuation Timelines:" dropdown. Then in the dropdown next to it, you can choose an actuation time to autofill the start time for the plot and the end time will be filled with the actuation time right after the one you chose.
3. If you choose not to use actuation times for your start and end times, you can manually enter these times. As done in the previous tool enter the start time and end time in seconds into their respective entry boxes.
4. Now you must choose what data you wish to plot. You can choose a sensor name under the "Left Axis" and "Right Axis" and you can also plot multiple sensors under the left or right axis so long as they have the same unit. You can add more or fewer sensors on one axis by clicking the plus or minus button.
5. Next choose whether you want to add vertical asymptotes for actuation times to your plot by selecting actuators under the "Actuators" title. You can add or remove actuators by using the plus or minus buttons. Note: if you leave the left and right axis as "None" and choose an actuator it will plot the actuator as data and not a vertical asymptote.
6. Finally, choose whether to save the plot automatically on creation by clicking the "Yes or "No" radio buttons.
7. Click "Create Plot" and your new custom plot will be generated.

![image](https://github.com/user-attachments/assets/45ce57aa-7b98-4025-afd2-b49e90093c46)

##### Export Parsed Data
   This tool allows you to export the parsed and processed data produced by the program to CSV. You may also choose a start and stop time to be returned in the CSV. The steps below describe how to use the tool:
1. If you wish to only get portions of the data in a CSV, you can choose to add a start time and end time for the data. Add these times in seconds in the "Start Time" and "End Time:" entry boxes.
2. Then click "Export Data" and the parsed data will be saved into the "\raw" subfolder under the names "parsed_sensor_data.csv" and "parsed_actuator_data.csv".

![image](https://github.com/user-attachments/assets/3d4cf10b-61c1-46de-baae-534c9c1bbfd3)

##### Custom Dataset
   This tool is useful for creating new datasets based on already existing data. You can subtract, add, multiply, or divide data from two different sensors. Examples of uses for this are to get the pressure difference between two different sensors or to get the pressure ratio between two sensors. After running this tool you can then plot this data using the custom plot tool or the replot all tool. To use the tool follow the below steps:
1. First, choose a name for the new dataset and enter it into the "New Dataset Name:" field. This will be the name when custom plotting and in graphs. If you are calculating a differential in pressure start the dataset name with "dP" or "P", as this will ensure it can be plotted on the same axis as other pressure values. Note the robustness of the program to recognize what type of data is in a dataset based on its name is not very robust. Atypical names may not plot with the correct units or be allowed to plot with other datasets/sensors. If you run into bugs with naming please reach out.
2. Next in the box containing dropdowns, choose your first sensor data to be used under "Data 1". Then choose the operation you want to use in the dropdown under the "Operator" title. Under the "Data 2" title, choose the second sensor data you want to be used in the calculation. Note the calculation will happen exactly as it appears in the tool and the calculation is done between each datapoint of each dataset.
3. Once you are happy with your decision click "Create Dataset". This will create the new dataset and add it to the program's stored data frame.

![image](https://github.com/user-attachments/assets/12ed018b-eb53-46c4-bd2a-7162cd07ec1d)

##### Engine Calculations
   **This tool is still under testing.** This tool is meant to do engine calculations based on thrust data collected from testing. The tool uses thrust data, and mass flow rate data from both an ox tank and fuel tank and determines the impulse, specific impulse, exhaust velocity and delta-V of the engine both instantaneous and average. It does this by doing a step-by-step calculation for each data point or an average over all points. To use this tool:
1. First enter the wet mass of the rocket in the entry box next to "Wet Mass (kg)". This is the planned mass of the rocket fully fueled in kg. Then enter the dry mass of the rocket in the entry box next to the "Dry Mass (kg)" label. The dry mass is the planned mass of the rocket after the engine uses all its fuel. These values are very important for determining the delta-V and also for the average value calculations.
2. Now enter the start time for the engine burn in the entry box next to the "Start Time:" label.
3. Then enter the end time for the engine burn in the entry box next to the "End Time:" label. It is important to get the start and end times right as it removes any of the non-burn time data from the results.
4. The last option is to choose whether you want to save the plots automatically after they are generated.  
5. Finally click "Run" and the program will calculate the results. The plots will be generated and average results will be filed in the results window.

![image](https://github.com/user-attachments/assets/a8faa875-3840-456c-ab3c-cccce2c1dd62)


#### Secondary Pages

##### Logs
   By clicking on the "Logs" button a new page will pop up which contains the logs generated by the program while it's running. This will show any errors and informational log entries made by the program to the program.log file. 
   
![image](https://github.com/user-attachments/assets/3868b24e-41f6-426b-904f-0dbefc19dc2e)

##### Settings
   By clicking on the "Settings" a new page will pop up called "Settings" which allows you to customize some parts of the program. The below settings are available:
**Differentiation Half Step Size** - This is the time in milliseconds that the program will use for the backward and forward steps used in the centring differentiation to get mass flow rate.
**Integration Method** - This is the integration method used by the program for doing numerical integration on a dataset. There are two methods Simpson's and the trapezoidal method. Simpson's tends to be more accurate than the trapezoidal method. Integration is used in a couple of the program's calculations for determining engine characteristics from thrust data.
**Integration Step Size** - This is the forward step size in milliseconds used by the program in integration. Regardless of the integration method used.
**Visual Mode** - This is a switch which allows you to set the program in dark or light mode.

![image](https://github.com/user-attachments/assets/7c5dafef-fcc2-4a74-a89b-83d1ca821463)


## Contributing

We welcome contributions to the project! If you want to add new features or make improvements, please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Create a pull request detailing the changes you have made.

## Suggested Updates / Next Steps

Here are some suggested updates and next steps for the project:

1. **Add Unit Handling System** Have the user assign a unit to each sensor when they use the custom dataset creator tool so that units and plotting can be handled more gracefully. Would remove chunky blocks of code which currently try to sort sensors by type of dimension. 
2. **Improve Graph Color System**: Improve the amount of colors available for use in lines on a plot which will increase the number of lines that can be plotted at once. Also, add error handling for this. It would be nice to make the vertical asymptote for actuators a specific shade of one colour so they differ from sensor lines.
3. **Modularize Visuals**: Add more modularity to the UI's visuals by making chunks of it into customized objects.
4. **Improved Error Handling**: Enhance the application to handle various error scenarios gracefully.
5. **Performance Optimization**: Optimize the log processing and plotting to handle larger datasets efficiently. Multiprocessing may help in some scenarios. 
