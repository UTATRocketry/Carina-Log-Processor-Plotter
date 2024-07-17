
import os
import multiprocessing
import pandas as pd
from queue import Queue
from . import parse_tools


def init(input_test_dir):
    global test_dir
    test_dir = input_test_dir


def has_been_parsed(test_dir):
    return os.path.exists(os.path.join(os.getcwd(), ".cache", test_dir, "sensors.csv")) and os.path.exists(os.path.join(os.getcwd(), ".cache", test_dir, "actuators.csv"))

def parse_from_raw(queue: Queue = None):
    sensor_lines = []
    with open(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", test_dir, "raw", "data.log"), "r") as data:
        sensor_lines = data.readlines()
    if queue: queue.put(2)

    actuator_lines = []
    with open(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", test_dir, "raw", "events.log"), "r") as event:
        actuator_lines = event.readlines()
    if queue: queue.put(3)

    time_offset = parse_tools.get_seconds_hhmmss(parse_tools.split_space_comma(actuator_lines[0])[1])
   
    num_cores = max(1, multiprocessing.cpu_count() - 4)
    segment_size = len(sensor_lines) // num_cores
    with multiprocessing.Pool(num_cores) as pool:
        segments = [(sensor_lines[i * segment_size:(i + 1) * segment_size], time_offset) for i in range(num_cores)]
        if len(sensor_lines) % num_cores != 0:
            segments.append((sensor_lines[num_cores * segment_size:], time_offset))

        results = pool.starmap(parse_sensor_lines, segments)
    
    sensors = results[0]
    i = 1
    while i < len(results):
        for sensor_name, data in results[i].items():
            if sensor_name in sensors:
                sensors[sensor_name].extend(data)
            else:
                sensors[sensor_name] = data
        i += 1
    if queue: queue.put(4)

    actuators = parse_actuator_lines(actuator_lines, time_offset)

    return sensors, actuators

def parse_sensor_lines(lines, time_offset):
    sensors = {}
    for line in lines:
        line_split = parse_tools.split_space_comma(line)
        time_hhmmss = line_split[1]
        time_ms = line_split[2]
        sensor_name = line_split[5]
        sensor_value = line_split[6]

        time = parse_tools.get_seconds_hhmmss(time_hhmmss) + float(time_ms) / 1000 - time_offset
        if time < 0:
            time += 86400   

        value = float(sensor_value[:-1])

        if sensor_name not in sensors:
            sensors[sensor_name] = [(time, value)]
        else:
            sensors[sensor_name].append((time, value))

    return sensors

def parse_actuator_lines(lines, time_offset):
    actuators = {}
    for line in lines:
        # Ignore extra lines
        if "ON" not in line and "OFF" not in line and "rotated" not in line:
            continue

        line_split = parse_tools.split_space_comma(line)
        time_hhmmss = line_split[1]
        time_ms = line_split[2]
        time = parse_tools.get_seconds_hhmmss(time_hhmmss) + float(time_ms)/1000 - time_offset
        if (time < 0):
            time += 86400

        actuator_name = ""
        actuator_value = 0
        
        if "rotated" in line:
            actuator_name = line_split[9].replace(":", "")
            actuator_value = line_split[-2]
        else:
            actuator_name = line_split[6].replace("'", "")
            actuator_value = 1 if ("ON" in line_split[-1]) else 0

        if actuator_name not in actuators:
            actuators[actuator_name] = [(time, actuator_value)]
        else:
            actuators[actuator_name].append((time, actuator_value))

    # Assign values of '' to all actuators at each time step they don't have a preexisting value
    for actuator in actuators:
        time_values = [val[0] for val in actuators[actuator]]
        for other_actuator in actuators:
            if other_actuator == actuator:
                continue
            other_time_values = [val[0] for val in actuators[other_actuator]]
            for time in time_values:
                if time not in other_time_values:
                    actuators[other_actuator].append((time, ""))
    for actuator in actuators:
        actuators[actuator].sort(key=lambda x: x[0])
            
    return actuators

def mass_flow_rate(sensors: pd.DataFrame, start_ind: int, end_ind: int) -> list: 
    time = sensors["Time"].to_list()[start_ind:end_ind]
    if "MFT" in sensors.columns:
        mass = sensors["MFT"].to_list()[start_ind:end_ind]
    else:
        mass = sensors["MOT"].to_list()[start_ind:end_ind]

    mass_flow = []
    for i in range(len(mass)):
        inds = indexes_from_ms(1500, i, time) # maybe add multiprocessing
        res = (mass[inds[1]] - mass[inds[0]]) / (time[inds[1]] - time[inds[0]])
        mass_flow.append(res)

    return mass_flow

def actuators_reformat(actuators: dict) -> None: 
    for actuator in actuators:
        state = 0
        for i in range(len(actuators[actuator])):
            if actuators[actuator][i][1] != "": 
                if int(actuators[actuator][i][1]) >= 1:
                    state = 1
                elif int(actuators[actuator][i][1]) == 0:
                    state = 0
            actuators[actuator][i] = (actuators[actuator][i][0], state)

def fill_actuators(time: list, actuators: dict)->dict:
    new_dict = {}
    for name in actuators.keys():
        if name == "Time":
            continue
        actuator = actuators[name]
        new_list = []
        prev_value = actuator[0][1]
        l = len(actuator)
        j = 0
        for i in range(len(time)):
            if j >= l:
                new_list.append((time[i], prev_value))
            elif time[i] < actuator[j][0]:
                new_list.append((time[i], prev_value))
            else:
                new_list.append((actuator[j][0], actuator[j][1]))
                prev_value = actuator[j][1]
                j += 1
        new_dict[name] = new_list
    return new_dict

def dataframe_format(sensors: dict, actuators: dict):
    # Create a Pandas DataFrame with column names as the sensor and actuator names
    sensor_df = pd.DataFrame(columns=["Time"] + list(sensors.keys()))
    sensor_df["Time"] = [val[0] for val in sensors[list(sensors.keys())[0]]]
    for sensor in sensors:
        sensor_df[sensor] = [val[1] for val in sensors[sensor]]

    actuators_reformat(actuators)
    actuators = fill_actuators(sensor_df["Time"].to_list(), actuators)
    actuator_df = pd.DataFrame(columns=["Time"] + list(actuators.keys()))
    actuator_df["Time"] = [val[0] for val in actuators[list(actuators.keys())[0]]]
    for actuator in actuators:
        actuator_df[actuator] = [val[1] for val in actuators[actuator]]

    return sensor_df, actuator_df

def indexes_from_ms(time_ms: int, cur_ind: int,  time: list) -> (tuple):
    ms = time_ms/1000
    i = cur_ind
    while i < len(time) and time[i] - time[cur_ind] < ms:
        i += 1
    j = cur_ind
    while j >= 0 and time[cur_ind] - time[j] < ms:
        j -= 1

    return (j, min(i, len(time) - 1))