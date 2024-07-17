import pandas as pd

def set_parameters(hs_size: int)->None:
    global diff_step_size
    diff_step_size = hs_size


def mass_flow_rate(sensors: pd.DataFrame, start_ind: int, end_ind: int) -> list: 
    time = sensors["Time"].to_list()[start_ind:end_ind]
    if "MFT" in sensors.columns:
        mass = sensors["MFT"].to_list()[start_ind:end_ind]
    else:
        mass = sensors["MOT"].to_list()[start_ind:end_ind]

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