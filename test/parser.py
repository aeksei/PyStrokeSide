from datetime import datetime
import pandas as pd
from pyrow.csafe import csafe_dic


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
    """
    Example: pd.DataFrame(get_raw_data(LOG_FILE)).to_csv('set_up_ergs.txt', header=False, index=False)
    :param file:
    :param start:
    :param finish:
    :return:
    """
    data = []
    start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S,%f")
    finish_date = datetime.strptime(finish, "%Y-%m-%d %H:%M:%S,%f")
    with open(file, "r") as f:
        for line in f:
            if line[-1] == '\n':
                line = line[:-1]
            if "DEBUG" in line:
                time = line.split(" raw          DEBUG    ")[0]
                cmd = line.split(" raw          DEBUG    ")[1]
                dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S,%f")
                if start_date <= dt <= finish_date:
                    data.append(cmd)

    return data


def raw_cmd_to_csv(file, save_file=False):
    """
    Convert raw commands to Pandas DataFrame
    save_file: True if need save to csv

    example: raw_cmd_to_csv('team.race', save_file=True)

    :return: Pandas DataFrame
    """

    columns = ['dst', 'src', 'common_cmd', 'len', 'id_cmd', 'cmd', 'data']
    df = pd.DataFrame(columns=columns)

    with open(file, 'r') as f:
        for s in f:
            raw_cmd = s[:-1].split(" ")

            line = {}
            i = 2
            line['dst'] = raw_cmd[i]

            i += 1  # 3
            line['src'] = raw_cmd[i]

            i += 1  # 4
            # skip status answer
            if raw_cmd[i] == '81' or raw_cmd[i] == '01':
                i += 1
            line['common_cmd'] = raw_cmd[i]

            i += 1
            line['len'] = raw_cmd[i]

            i += 1
            line['id_cmd'] = raw_cmd[i]
            line['cmd'] = csafe_dic.race_cmds[int(line['id_cmd'], 16)]

            i += 1
            line['data'] = raw_cmd[i:-2]

            df = df.append(line, ignore_index=True)

    if save_file:
        df.to_csv("pandas\\" + file, columns=columns)

    return df


if __name__ == "__main__":
    path = "LogData\\RawCommands\\"
    LOG_FILE = path + "RawCommands.log"

    raw_cmd_to_csv('set_up_ergs.txt', save_file=True)







