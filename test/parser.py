import os
from datetime import datetime


def parse_update_race_data(file):
    data = []
    with open(file, "r") as f:
        for line in f:
            if "DEBUG    resp from update_race_data:" in line:
                time = line.split(" __")[0]
                resp = line.split(": ")[1][1:-2].replace(" ", "").split(",")
                data.append([time, resp])
    return data


def parse_set_race_lane_setup(file):
    data = []
    with open(file, "r") as f:
        for line in f:
            if "DEBUG" in line:
                cmd = line.split("[")[1][:-2]
                cmd = " ".join([hex(int(i))[2:].rjust(2, "0") for i in cmd.split(", ")])
                print(cmd)
    return data


def get_raw_data(file, start="1900-01-01 00:00:00,000", finish="2100-01-01 00:00:00,000"):
    data = []
    start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S,%f")
    finish_date = datetime.strptime(finish, "%Y-%m-%d %H:%M:%S,%f")
    for line in file:
        if line[-1] == '\n':
            line = line[:-1]
        if "DEBUG" in line:
            time = line.split(" raw          DEBUG    ")[0]
            cmd = line.split(" raw          DEBUG    ")[1]
            dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S,%f")
            if start_date <= dt <= finish_date:
                data.append(cmd)

    return data


if __name__ == "__main__":
    path = "test\\LogData\\RawCommands\\"
    LOG_FILE = path + "RawCommands.log"
    # data_log = parse_update_race_data(LOG_FILE)

    #LOG_FILE = "tmp.txt"
    #data_log = parse_set_race_lane_setup(LOG_FILE)

    """
    with open("tmp.txt", "w") as f:
        start_race = datetime.strptime("2019-02-24 10:59:36,862", "%Y-%m-%d %H:%M:%S,%f")
        finish_race = datetime.strptime("2019-02-24 11:08:49,645", "%Y-%m-%d %H:%M:%S,%f")

        for data in data_log:
            time = data[0]
            dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S,%f")
            if start_race <= dt <= finish_race:
                resp = [int(i) for i in data[1]]
                hex_cmd = " ".join([hex(c)[2:].rjust(2, "0") for c in resp])
                f.write(hex_cmd)
                f.write("\n")
    """

    with open(LOG_FILE, 'r') as raw_log:
        data = get_raw_data(raw_log)

        with open('test\\tmp.txt', 'w') as f:
            for d in data:
                f.write(d)
                f.write('\n')


