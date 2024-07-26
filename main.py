import pandas
from CarinaLogProcessorPlotter import Carina_Log_Processor_Plotter

# Name of program that will be used in Window that opens
NAME = "Carina Data Proccesor & Plotter"

if __name__ == "__main__":
    pandas.options.mode.chained_assignment = None # removes pandas warning that is a false positive  
    app = Carina_Log_Processor_Plotter.CarinaLogProcessorPlotter(NAME) #Start program by initializing main object
  