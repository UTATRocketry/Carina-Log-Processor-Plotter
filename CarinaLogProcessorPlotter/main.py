import pandas
from Carina_Log_Processor_Plotter import Carina_Log_Processor_Plotter

NAME = "Carina Data Proccesor & Plotter"

if __name__ == "__main__":
    pandas.options.mode.chained_assignment = None 
    app = Carina_Log_Processor_Plotter(NAME)
  