
# Carina Log Processor and Plotter

## Overview

The Carina Log Processor and Plotter is a GUI-based application designed to read, process, and visualize log data from Carina. The application provides a user-friendly interface for selecting data folders, configuring plot settings, and generating plots.

## Features

- **Data Input**: Specify the folder containing the data and event logs.
- **Visualization**: Generate and save plots based on the processed log data.
- **Customization**: Use our UI to make multi-sensor plots of your choosing and add actuation time as vertical asymptotes on the plot.   
- **Log Management**: View and manage application logs within the GUI.
- **Dark Mode**: Toggle between light and dark modes for better visibility and user preference.

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

## Usage

1. Open the application.
2. Enter the folder name that contains the data and event logs.
3. Choose whether to save the initial plots or not.
4. Click the "Start Program" button to process and visualize the data across the entire time domain.
5. Now use the UI to customize the plots as you need to perform your data analysis. In addition, you can use the tool to numerically solve for the mass flow rate and plot it as well. 

### Start Page 
![image](https://github.com/user-attachments/assets/e2d9a487-77e9-4db8-8e27-596e9e0c69fc)
### Main Program
![image](https://github.com/user-attachments/assets/44cf4a4d-e7fa-465b-a164-866577a4a676)

## Contributing

We welcome contributions to the project! If you want to add new features or make improvements, please follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Create a pull request detailing the changes you have made.

## Suggested Updates / Next Steps

Here are some suggested updates and next steps for the project:

1. **Configurations Page**: Add a button to the UI in the same box as the "Return" and "Log" buttons. This button would bring the user to a different page and this would allow them to configure certain values used in the program such as the "h" used when differentiating the mass into mass flow rate.
2. **Improve Graph Color System**: Improve the amount of colors available for use in lines on a plot which will increase the number of lines that can be plotted at once. Also, add error handling for this. It would be nice to make the vertical asymptote for actuators a specific shade of one colour so they differ from sensor lines.
3. **Create Ability to Deal with Thrust Data**: Be able to use the thrust from hot fire tests to calculate impulse, exhaust velocity, specific impulse, and Delta V. Maybe Add a separate frame for this
4. **Data Operations Tool** Add frame that allows you to customly perform operation between two data sets e.g.PFM - PCC. This would produce a new dataset you could then plot.
5. **Modularize Visuals**: Add more modularity to the UI's visuals by making chunks of it into customized objects.
6. **Improved Error Handling**: Enhance the application to handle various error scenarios gracefully.
7. **Performance Optimization**: Optimize the log processing and plotting to handle larger datasets efficiently. Multiprocessing may help in some scenarios. 
