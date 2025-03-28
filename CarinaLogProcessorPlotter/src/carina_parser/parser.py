
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
    if queue: queue.put(2) # al queue puts are for the progress bar in UI

    actuator_lines = []
    with open(os.path.join(os.getcwd(), "CarinaLogProcessorPlotter", "Data", test_dir, "raw", "events.log"), "r") as event:
        actuator_lines = event.readlines()
    if queue: queue.put(3)

    time_offset = parse_tools.get_seconds_hhmmss(parse_tools.split_space_comma(actuator_lines[0])[1])
   
   # Multiprocessing to speed up sensor parsing
    num_cores = max(1, multiprocessing.cpu_count() - 4)
    segment_size = len(sensor_lines) // num_cores
    with multiprocessing.Pool(num_cores) as pool:
        segments = [(sensor_lines[i * segment_size:(i + 1) * segment_size], time_offset) for i in range(num_cores)]
        if len(sensor_lines) % num_cores != 0:
            segments.append((sensor_lines[num_cores * segment_size:], time_offset))

        results = pool.starmap(parse_sensor_lines, segments)
    
    # Combining results form multiprocessing
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

def actuators_reformat(actuators: dict) -> None: 
    '''Converts degree measurments into on and off (1/0)'''
    for actuator in actuators:
        state = 0
        max_val = -1000
        min_val = 1000
        for i in range(len(actuators[actuator])): # Finds max and min value of actuator
            if actuators[actuator][i][1] != "":
                if int(actuators[actuator][i][1]) > max_val:
                    max_val = int(actuators[actuator][i][1])
                if int(actuators[actuator][i][1]) < min_val:
                    min_val = int(actuators[actuator][i][1])
        #Uses max min to find points of change in logs
        for i in range(len(actuators[actuator])): 
            if actuators[actuator][i][1] != "":
                if int(actuators[actuator][i][1]) == max_val: 
                    state = 1 if actuator[0:2] != "BV" else 0
                elif int(actuators[actuator][i][1]) == min_val:
                    state = 0 if actuator[0:2] != "BV" else 1
                actuators[actuator][i] = (actuators[actuator][i][0], state)

                #Outdated left here incase needed again
                # if actuator[0:2] == 'BV':
                #     if int(actuators[actuator][i][1]) == 100: 
                #         state = 0
                #     elif int(actuators[actuator][i][1]) == 0:
                #         state = 1
                # if actuator == "MFV":
                #     if int(actuators[actuator][i][1]) >= 10: 
                #         state = 1
                #     else:
                #         state = 0
                # else:
                #     if int(actuators[actuator][i][1]) >= 1: 
                #         state = 1
                #     elif int(actuators[actuator][i][1]) == 0:
                #         state = 0

            

def fill_actuators(time: list, actuators: dict)->dict:
    '''Fills/extends each actuator in the dictionary with a value for all the time values that are in the sensor dictionary making all the lsits the same size.'''
    new_dict = {}
    for name in actuators.keys():
        if name == "Time":
            continue
        actuator = actuators[name]
        new_list = []
        for tuple in actuator:
            if tuple[1] != '':
                prev_value = tuple[1]
                break
        l = len(actuator)
        j = 0
        for i in range(len(time)):
            if j >= l:
                new_list.append((time[i], prev_value))
            elif time[i] < actuator[j][0]:
                new_list.append((time[i], prev_value))
            else:
                new_list.append((actuator[j][0], actuator[j][1]) if actuator[j][1] != '' else (actuator[j][0], prev_value))
                if actuator[j][1] != '':
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
    
    if len(actuators) == 0:
        return sensor_df, pd.DataFrame({"Time": sensor_df["Time"], "Empty": [0]*len(sensor_df["Time"])})
    actuators_reformat(actuators)
    actuators = fill_actuators(sensor_df["Time"].to_list(), actuators)
    actuator_df = pd.DataFrame(columns=["Time"] + list(actuators.keys()))
    actuator_df["Time"] = [val[0] for val in actuators[list(actuators.keys())[0]]]
    for actuator in actuators:
        actuator_df[actuator] = [val[1] for val in actuators[actuator]]
    return sensor_df, actuator_df


