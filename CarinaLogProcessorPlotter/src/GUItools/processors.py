
import pandas as pd
import math
from scipy.integrate import simpson

def set_parameters(hs_size: int, int_method: str, step_size: int)->None:
    global diff_step_size, int_step_size, integration_method
    diff_step_size = hs_size
    int_step_size = step_size
    integration_method = int_method

def engine_calculations(sensors_df: pd.DataFrame, start: int, end: int)->list:
    pass


def mass_flow_rate(sensor: str, sensors: pd.DataFrame, start_ind: int, end_ind: int) -> list: 
    time = sensors["Time"].to_list()[start_ind:end_ind]
    mass = sensors[sensor[1:]].to_list()[start_ind:end_ind]

    mass_flow = []
    for i in range(len(mass)):
        inds = indexes_from_ms(diff_step_size, i, time) # maybe add multiprocessing
        res = (mass[inds[1]] - mass[inds[0]]) / (time[inds[1]] - time[inds[0]])
        mass_flow.append(res)

    return mass_flow


def indexes_from_ms(time_ms: int, cur_ind: int,  time: list) -> (tuple):
    ms = time_ms/1000
    i = cur_ind
    while i < len(time) and time[i] - time[cur_ind] < ms:
        i += 1
    j = cur_ind
    while j >= 0 and time[cur_ind] - time[j] < ms:
        j -= 1

    return (j, min(i, len(time) - 1))

def index_from_ms(time_ms:int, cur_ind, time) -> int:
    ms = time_ms/1000
    i = cur_ind
    while i < len(time) and time[i] - time[cur_ind] < ms:
        i += 1
    return min(i, len(time) - 1)


def trapezoid_integration(sensor: list, time: list)->float:
    res = 0
    for i in range(len(time) - 1):
        ind = index_from_ms(int_step_size, i, time)
        res += ((sensor[i] + sensor[ind])/2) * (time[ind] - time[i])

    return res

def simpson_integration(sensor: list, time: list)->float:
    return simpson(sensor, time, int_step_size)

def specific_impulse_avg(impulse: list, mass:list) -> float:
    G = 9.90665
    return impulse/(mass*G)

def specific_impulse_instataneous(thrust: list, mass_flow_rate: list) -> list:
    G = 9.90665
    isp = []
    for i in range(len(thrust)):
        isp.append(thrust[i]/(mass_flow_rate[i] * G))
    return isp

def exhaust_velocity_instantaneous(thrust: list, mass_flow_rate: list) -> list:
    v_exhaust = []
    for i in range(len(thrust)):
        v_exhaust.append(thrust[i]/mass_flow_rate[i])
    return v_exhaust

def exhaust_velocity_avg(impulse: list, mass:list) -> float:
    return impulse/mass

def delta_v(exhaust_velocity: float, initial_mass: float, final_mass: float):
    return exhaust_velocity * math.log(initial_mass/final_mass)

if __name__ == "__main__":
    set_parameters(1000, 1000)
    y = [2, 2, 6, 20]
    x = [0, 1, 2, 3]
    print(trapezoid_integration(y, x))
    print(simpson(y, x, 1))