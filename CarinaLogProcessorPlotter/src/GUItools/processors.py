
import pandas as pd
import math
from scipy.integrate import simpson

def set_parameters(hs_size: int, int_method: str, step_size: int)->None:
    '''Initializes/Sets global variables used in different functions. These are configurable settings through the UI'''
    global diff_step_size, int_step_size, integration_method
    diff_step_size = hs_size
    int_step_size = step_size
    if int_method == "Simpson":
        integration_method = simpson_integration
    elif int_method == "Trapezoid":
        integration_method = trapezoid_integration
        

def engine_calculations(sensors_df: pd.DataFrame, initial_mass: float, final_mass: float, start_ind: int, end_ind: int)->list:
    time = sensors_df["Time"].to_list()[start_ind:end_ind]
    propellant_mass = initial_mass - final_mass

    mass_flow_fuel = mass_flow_rate("MFT", sensors_df, start_ind, end_ind)
    mass_flow_ox = mass_flow_rate("MOT", sensors_df, start_ind, end_ind)
    mass_flow_total = []
    for i in range(len(mass_flow_fuel)):
        mass_flow_total.append(mass_flow_fuel[i] + mass_flow_ox[i])

    thrust_sensor_name = "TLC" # chnage as nescesaary
    thrust = sensors_df[thrust_sensor_name].to_list()[start_ind:end_ind]
    for val in thrust:
        val *= 9.80665
    impulse = integration_method(thrust, time)
    inst_isp = specific_impulse_instataneous(thrust, mass_flow_total)
    inst_ve = exhaust_velocity_instantaneous(thrust, mass_flow_total)
    inst_dv = delta_v_instantaneous(inst_ve, initial_mass, final_mass)

    avg_isp = specific_impulse_avg(impulse, propellant_mass)
    avg_ve = exhaust_velocity_avg(impulse, propellant_mass)
    avg_dv = delta_v_avg(avg_ve, initial_mass, final_mass)
    
    return [("dMFT", mass_flow_fuel), ("dMOT", mass_flow_ox), ("dM", mass_flow_total), ("THRUST", thrust), ("Impulse", impulse), ("ISP", inst_isp), ("Exhaust Velocity", inst_ve), ("Delta V", inst_dv), ("Avg ISP", avg_isp), ("Avg Exhaust Velocity", avg_ve), ("Avg Delat V", avg_dv)]


def mass_flow_rate(sensor: str, sensors: pd.DataFrame, start_ind: int, end_ind: int) -> list:
    '''Calculates mass flow rate by using sensor in the datrafram and diferentiating it's data using centering differenciation'''
    time = sensors["Time"].to_list()[start_ind:end_ind]
    mass = sensors[sensor[1:]].to_list()[start_ind:end_ind]

    mass_flow = []
    for i in range(len(mass)):
        inds = indexes_from_ms(diff_step_size, i, time) # maybe add multiprocessing
        res = (mass[inds[1]] - mass[inds[0]]) / (time[inds[1]] - time[inds[0]])
        mass_flow.append(res)

    return mass_flow


def indexes_from_ms(time_ms: int, cur_ind: int,  time: list) -> (tuple):
    '''Takes in a time in ms and returns the index which is closests to that many ms away from the curent index supplied forward and backward''' 
    ms = time_ms/1000
    i = cur_ind
    while i < len(time) and time[i] - time[cur_ind] < ms:
        i += 1
    j = cur_ind
    while j >= 0 and time[cur_ind] - time[j] < ms:
        j -= 1

    return (j, min(i, len(time) - 1))

def index_from_ms(time_ms:int, cur_ind, time) -> int:
    '''Takes in time in ms and returns the index that many ms away from the current index in only the forward direction'''
    ms = time_ms/1000
    i = cur_ind
    while i < len(time) and time[i] - time[cur_ind] < ms:
        i += 1
    return min(i, len(time) - 1)


def trapezoid_integration(sensor: list, time: list)->float:
    '''Takes in data list and performs trapezoidal integration on it'''
    res = 0
    for i in range(len(time) - 1):
        ind = index_from_ms(int_step_size, i, time)
        res += ((sensor[i] + sensor[ind])/2) * (time[ind] - time[i])
    return res

def simpson_integration(sensor: list, time: list)->float:
    '''Takes in data list and uses pandas simpson integration method'''
    return simpson(sensor, time, int_step_size)

def specific_impulse_avg(impulse: list, propellant_mass:list) -> float:
    '''Calculates average specific impulse from impulse and total propellant mass'''
    G = 9.90665
    return impulse/(propellant_mass*G)

def specific_impulse_instataneous(thrust: list, mass_flow_rate: list) -> list:
    '''Calculates specific impulse for each data point of thrust and returns lsit of instantaneous specific impusle at a given time'''
    G = 9.90665
    isp = []
    for i in range(len(thrust)):
        isp.append(thrust[i]/(mass_flow_rate[i] * G))
    return isp

def exhaust_velocity_instantaneous(thrust: list, mass_flow_rate: list) -> list:
    '''Calculates exhaust velocity for each data point of thrust and returns lsit of instantaneous exhaust velocity at a given time'''
    v_exhaust = []
    for i in range(len(thrust)):
        v_exhaust.append(thrust[i]/mass_flow_rate[i])
    return v_exhaust

def exhaust_velocity_avg(impulse: list, propellant_mass:list) -> float:
    '''Calculates average exhaust from impulse and total propellant mass'''
    return impulse/propellant_mass

def delta_v_avg(exhaust_velocity: float, initial_mass: float, final_mass: float):
    '''Calculates average delta V from avg exhaust velocity and dry and wet mass of rocket'''
    return exhaust_velocity * math.log(initial_mass/final_mass)

def delta_v_instantaneous(exhaust_velocity: list, initial_mass: float, final_mass: float):
    '''Calculates delta V for each data point of instantaneuos exhaust velocity and returns lsit of instantaneous delata V at a given time'''
    dv = []
    for val in exhaust_velocity:
        dv.append(val * math.log(initial_mass/final_mass))
    return dv

def custom_dataset(sensor1: str, sensor2: str, dataframe: pd.DataFrame, opt: str) -> list:
    '''calculates new dataset based on operation betwene two toher datasets'''
    data1 = dataframe[sensor1].to_list()
    data2 = dataframe[sensor2].to_list()
    new_dataset = []
    for i in range(len(data1)):
        if opt == "+":
            new_dataset.append(data1[i] + data2[i])
        elif opt == "-":
            new_dataset.append(data1[i] - data2[i])
        elif opt == "x":
            new_dataset.append(data1[i] * data2[i])
        elif opt == "/":
            new_dataset.append(data1[i] / data2[i])
    return new_dataset
