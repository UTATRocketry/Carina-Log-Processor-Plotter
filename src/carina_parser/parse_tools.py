
def get_seconds_hhmmss(time_formatted):
    time_formatted = time_formatted.split(":")
    time_formatted = [int(t) for t in time_formatted]
    return time_formatted[0]*3600 + time_formatted[1]*60 + time_formatted[2]
  

def split_space_comma(line):
    delim_1 = line.split(",")
    delim_2 = []
    for d in delim_1:
        delim_2.extend(d.split(" "))
    if ("'ENABLE" in delim_2):
        idx = delim_2.index("'ENABLE")
        delim_2.remove("'ENABLE")
        delim_2[idx] = "'ENABLE " + delim_2[idx]
    return delim_2