
import pandas as pd


def init(input_test_dir):
    global test_dir
    test_dir = input_test_dir


def write_to_cache(sensors, actuators):
    # Create a Pandas DataFrame with column names as the sensor and actuator names
    sensor_df = pd.DataFrame(columns=["Time"] + list(sensors.keys()))
    sensor_df["Time"] = [val[0] for val in sensors[list(sensors.keys())[0]]]
    for sensor in sensors:
        sensor_df[sensor] = [val[1] for val in sensors[sensor]]
    sensor_df.to_csv(".cache\\" + test_dir + "sensors.csv", index=False)

    actuator_df = pd.DataFrame(columns=["Time"] + list(actuators.keys()))
    actuator_df["Time"] = [val[0] for val in actuators[list(actuators.keys())[0]]]
    for actuator in actuators:
        actuator_df[actuator] = [val[1] for val in actuators[actuator]]
    actuator_df.to_csv(".cache\\" + test_dir + "actuators.csv", index=False)


def read_into_df():
    sensor_df = pd.read_csv(".cache\\" + test_dir + "sensors.csv")
    actuator_df = pd.read_csv(".cache\\" + test_dir + "actuators.csv")

    return sensor_df, actuator_df


def write_to_csv(sensor_df, actuator_df, time_range = (), name_suffix = ""):
    # Write the sensor and actuator data to a CSV file, if the time range is specified, only write the data within that range
    if time_range:
        sensor_df = sensor_df[(sensor_df["Time"] >= time_range[0]) & (sensor_df["Time"] <= time_range[1])]
        actuator_df = actuator_df[(actuator_df["Time"] >= time_range[0]) & (actuator_df["Time"] <= time_range[1])]
    if name_suffix:
        name_suffix = "_" + name_suffix
    sensor_df.to_csv("Data\\" + test_dir + "compiled\\sensors" + name_suffix + ".csv", index=False)
    actuator_df.to_csv("Data\\" + test_dir + "compiled\\actuators" + name_suffix + ".csv", index=False)