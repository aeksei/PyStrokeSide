import os
import sys
import time
import json
import socketio
from datetime import datetime
from collections import Counter
from subprocess import Popen, PIPE

from config import Config
from config import _bytes2ascii, _bytes2int, _int2bytes
from loggers import logger, race_logger, raw_logger


class PyStrokeSide:
    _PATH_USBPCAP = r"C:\Program Files\USBPcap"
    command = r"USBPcapCMD.exe -d \\.\USBPcap1 -o - -A"
    LEN_BUF = 1

    def __init__(self):
        self.HOME_DIR = os.getcwd()
        self.race_file = None

        self.race_name = None
        self.erg_line = {}
        self.participant_name = {}
        self.total_distance = None
        self.race_data = {}
        self.race_team = 1
        self.team_data = {}

        self.address = None
        self.token = None
        self.timeout = 0

        self.logger = logger()
        self.config = Config()
        self.restore_config()

        self.race_logger = None
        self.new_race_logger()
        self.raw_logger = raw_logger()

        try:
            if self.address is not None:
                self.sio = socketio.Client()
                self.sio.connect(self.address)
                self.sio.emit('login', {'token': self.token})
                self.logger.info("Соединение с сервером установлено")
        except socketio.exceptions.ConnectionError:
            self.logger.critical(
                'Не удалось установить соединение с сервером. '
                'Проверьте интернет соединение или работоспособность сервера.')

        if "USBPcap" not in os.listdir(r"C:\Program Files"):
            self.logger.critical('Необходимо установить программу "USBPcap"')

    def new_race_logger(self):
        if self.race_file is None:
            self.race_file = "{}_{:%Y-%m-%d_%H-%M-%S}.log".format(self.race_name, datetime.now())

        if self.race_logger is None:
            self.race_logger = race_logger(self.race_file)
        else:
            handlers = self.race_logger.handlers[:]
            for handler in handlers:
                handler.close()
                self.race_logger.removeHandler(handler)
            self.race_file = "{}_{:%Y-%m-%d_%H-%M-%S}.log".format(self.race_name, datetime.now())
            self.race_logger = race_logger(self.race_file)

        self.logger.info("Init Race Log File: {}".format(self.race_file))

    def restore_config(self):
        self.address = self.config.address
        self.token = self.config.token

        self.total_distance = self.config.total_distance
        self.race_name = self.config.race_name
        self.race_file = self.config.race_file
        self.race_team = self.config.race_team

        self.erg_line = self.config.erg_line
        self.participant_name = self.config.participant_name

    def write_config(self):
        if self.address is not None:
            self.config['SERVER']['address'] = self.address
        if self.token is not None:
            self.config['SERVER']['token'] = self.token

        self.config['RACE']['total_distance'] = self.total_distance
        self.config['RACE']['race_name'] = self.race_name
        self.config['RACE']['race_file'] = self.race_file
        self.config['RACE']['race_team'] = self.race_team

        self.config['NUMERATION_ERG'] = {}
        for erg, line in self.erg_line.items():
            self.config['NUMERATION_ERG'][str(erg)] = line

        self.config['PARTICIPANT_NAME'] = {}
        for line, name in self.participant_name.items():
            self.config['PARTICIPANT_NAME'][str(line)] = name

        self.config.write()

    def check_team_race(self):
        count_member = (len(self.participant_name) / len(set(self.participant_name.values())))
        if count_member in [2, 4, 8]:
            self.race_team = int(count_member)
        else:
            self.race_team = 1

        self.race_data.clear()
        self.team_data.clear()



    def send_race_data(self):
        data = dict(timestamps=datetime.now().isoformat(sep=" ", timespec='seconds'),
                    race_name=self.race_name,
                    total_distance=self.total_distance,
                    race_data=list(self.race_data.values()))

        self.race_logger.info(json.dumps(data))

        if self.race_team != 1:
            for line in range(1, len(self.participant_name), self.race_team):  # sub race_data for each team
                sub_race_data = [self.race_data[l] for l in range(line, line+self.race_team)]
                common = Counter(sub_race_data[0])
                for c in sub_race_data[1:]:
                    common += Counter(c)
                team_lines = "-".join([str(line), str(line+self.race_team-1)])
                self.team_data[team_lines] = common
            print(self.team_data)
        else:
            self.logger.info(self.race_data)

        if self.address is not None:
            self.sio.emit('send_data', {'data': data})
            self.logger.info("send data to server")

        time.sleep(self.timeout)

    def set_race_participant_command(self, cmd):
        line = cmd[8]
        if cmd[2] == 0x01 and line == 0:  # name race
            self.race_name = _bytes2ascii(cmd[9:9 + cmd[7] - 2])

            self.logger.info("Start new race: {}".format(self.race_name))
            self.logger.debug(_int2bytes(cmd))

        elif cmd[2] == 0xFF:  # name participant
            if line == 0x01:
                self.participant_name.clear()
                self.logger.info("Clear participant name")
            self.participant_name[line] = _bytes2ascii(cmd[9:9 + cmd[7] - 2])

            self.logger.info("Lane {} have name: {}".format(line, self.participant_name[line]))
            self.logger.debug(_int2bytes(cmd))

    def set_race_lane_setup_command(self, cmd):
        if cmd[2] == 0x01:
            self.erg_line.clear()
            self.logger.info("Clear erg line")
        self.erg_line[cmd[2]] = cmd[8]

        self.logger.info("erg {} is lane: {}".format(cmd[2], cmd[8]))
        self.logger.debug(_int2bytes(cmd))

    def set_all_race_params_command(self, cmd):
        if cmd[2] == 0x01:
            self.total_distance = _bytes2int(cmd[30:34])
            self.logger.info("set distance: {}".format(self.total_distance))
            self.logger.debug(_int2bytes(cmd))

            self.new_race_logger()
            self.check_team_race()

            self.write_config()

    def update_race_data_response(self, resp):
        src = resp[3]
        if src == 0x01 and len(self.race_data) != 0:
            self.send_race_data()

        distance = round(_bytes2int(resp[14:18]) * 0.1, 1)  # dist * 10
        time = round(_bytes2int(resp[20:24]) * 0.01, 2)  # time * 100
        stroke = resp[24]  # stroke
        split = round(500 * (time / distance) if distance != 0 else 0, 2)

        erg_data = dict(line=self.erg_line[src],
                        participant_name=self.participant_name[self.erg_line[src]],
                        distance=distance,
                        time=time,
                        stroke=stroke,
                        split=split)
        self.race_data[self.erg_line[src]] = erg_data

        self.logger.info(erg_data)
        self.logger.debug(_int2bytes(resp))

    def handler(self, cmd):
        if cmd[4] == 0x76 and cmd[6] == 0x32:
            self.set_race_participant_command(cmd)
        elif cmd[4] == 0x7e and cmd[6] == 0x0b:
            self.set_race_lane_setup_command(cmd)
        elif cmd[5] == 0x76 and cmd[7] == 0x33:
            self.update_race_data_response(cmd)
        elif cmd[4] == 0x76 and cmd[6] == 0x1d:
            self.set_all_race_params_command(cmd)

    def sniffing(self):
        os.chdir(self._PATH_USBPCAP)
        process = Popen(self.command, stdout=PIPE, shell=True)
        self.logger.info("Open USBPcap")

        self.logger.info("Start sniffing")
        os.chdir(self.HOME_DIR)
        buffer = b""

        while True:
            buffer += process.stdout.read(self.LEN_BUF)
            if b"\x02\xf0" in buffer and b"\xf2" in buffer:
                cmd = buffer[buffer.find(b"\x02\xf0"):buffer.find(b"\xf2") + 1]
                if cmd:
                    self.raw_logger.debug(_int2bytes(cmd))
                    # Byte Staffing
                    while b"\xf3\x00" in cmd:
                        cmd = cmd.replace(b"\xf3\x00", b"\xf0")
                    while b"\xf3\x01" in cmd:
                        cmd = cmd.replace(b"\xf3\x01", b"\xf1")
                    while b"\xf3\x02" in cmd:
                        cmd = cmd.replace(b"\xf3\x02", b"\xf2")
                    while b"\xf3\x03" in cmd:
                        cmd = cmd.replace(b"\xf3\x03", b"\xf3")
                    self.handler([c for c in cmd])

            buffer = buffer[buffer.find(b"\xf2") + 1:]


if __name__ == "__main__":
    race = PyStrokeSide()
    try:
        race.sniffing()
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        race.logger.critical("{} {}".format(e, e.args))
    finally:
        race.logger.info("Close sniffer")
        sys.exit()

