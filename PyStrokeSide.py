import os
import time
import logging
import socketio
from datetime import datetime
from subprocess import Popen, PIPE
from logging.handlers import RotatingFileHandler

from config import Config
from config import _bytes2ascii, _bytes2int, _int2bytes

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

        self.address = None
        self.token = None
        self.timeout = 0

        self.logger = self.init_logger()
        self.config = Config()
        self.restore_config()

        self.race_logger = None
        if self.race_name is not None:
            self.init_race_logger(self.race_name)
        self.raw_logger = self.init_raw_logger()

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

    def init_logger(self):
        if "LogData" not in os.listdir():
            os.mkdir("LogData")
        if "Log" not in os.listdir(os.getcwd() + "\\LogData"):
            os.mkdir(os.getcwd() + "\\LogData" + "\\Log")

        logger = logging.getLogger("PyStrokeSide")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        path = os.getcwd() + "\\LogData" + "\\Log"
        filehandler = RotatingFileHandler(path + "\\PyStrokeSide.log",
                                          maxBytes=25 * 1024 * 1024,
                                          backupCount=50)

        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(filehandler)

        return logger

    def init_race_logger(self, filename=None):
        if self.race_logger is not None:
            handlers = self.race_logger.handlers[:]
            for handler in handlers:
                handler.close()
                self.race_logger.removeHandler(handler)

        self.race_logger = logging.getLogger("race")
        self.race_logger.setLevel(logging.INFO)

        if "RaceLog" not in os.listdir(os.getcwd() + "\\LogData"):
            os.mkdir(os.getcwd() + "\\LogData" + "\\RaceLog")
            self.logger.debug('Create "RaceLog" directory')

        path = os.getcwd() + "\\LogData" + "\\RaceLog" + "\\"
        if filename is None:
            self.race_file = "{}_{:%Y-%m-%d_%H-%M-%S}.log".format(self.race_name, datetime.now())
            self.logger.info("Init Race Log File: {}".format(self.race_file))
        else:
            self.logger.info("Restore Race Log File: {}".format(self.race_file))

        racehandler = logging.FileHandler(path + self.race_file)
        racehandler.setLevel(logging.DEBUG)
        self.race_logger.addHandler(racehandler)

    def init_raw_logger(self):
        if "RawCommands" not in os.listdir(os.getcwd() + "\\LogData"):
            os.mkdir(os.getcwd() + "\\LogData" + "\\RawCommands")

        raw_logger = logging.getLogger("raw")
        raw_logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

        path = os.getcwd() + "\\LogData" + "\\RawCommands" + "\\"
        filename = "RawCommands.log"
        filehandler = RotatingFileHandler(path + filename,
                                          maxBytes=25 * 1024 * 1024,
                                          backupCount=50)

        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        raw_logger.addHandler(filehandler)

        return raw_logger

    def restore_config(self):
        if self.config.filename not in os.listdir(self.HOME_DIR):
            self.config.create()
            self.logger.info("Create configure file {}".format(self.config.filename))
        else:
            if 'address' in self.config['SERVER']:
                self.address = self.config['SERVER']['address'] if self.config['SERVER']['address'] != '' else None
            if 'token' in self.config['SERVER']:
                self.token = self.config['SERVER']['token'] if self.config['SERVER']['token'] != '' else None

            self.total_distance = \
                self.config['RACE']['total_distance'] if self.config['RACE']['total_distance'] != '' else None
            self.race_name = self.config['RACE']['race_name'] if self.config['RACE']['race_name'] != '' else None
            self.race_file = self.config['RACE']['race_file'] if self.config['RACE']['race_file'] != '' else None

            for erg_num in self.config['NUMERATION_ERG']:
                self.erg_line[int(erg_num)] = self.config['NUMERATION_ERG'].as_int(erg_num)
            for line in self.config["PARTICIPANT_NAME"]:
                self.participant_name[int(line)] = self.config["PARTICIPANT_NAME"][line]

    def write_config(self):
        if self.address is not None:
            self.config['SERVER']['address'] = self.address
        if self.token is not None:
            self.config['SERVER']['token'] = self.token

        self.config['RACE']['total_distance'] = self.total_distance
        self.config['RACE']['race_name'] = self.race_name
        self.config['RACE']['race_file'] = self.race_file

        for erg, line in self.erg_line.items():
            self.config['NUMERATION_ERG'][str(erg)] = line

        for line, name in self.participant_name.items():
            self.config['PARTICIPANT_NAME'][str(line)] = name

        self.config.write()

    def send_race_data(self):
        data = dict(timestamps=datetime.now().isoformat(sep=" ", timespec='seconds'),
                    race_name=self.race_name,
                    total_distance=self.total_distance,
                    race_data=list(self.race_data.values()))

        if self.address is not None:
            self.sio.emit('send_data', {'data': data})
            self.logger.info("send data to server")

        self.race_logger.info(data)
        if self.timeout != 0:
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
            self.participant_name[line] = _bytes2ascii(cmd[9:9 + cmd[7] - 2])

            self.logger.info("Lane {} have name: {}".format(line, self.participant_name[line]))
            self.logger.debug(_int2bytes(cmd))

    def set_race_lane_setup_command(self, cmd):
        if cmd[2] == 0x01:
            self.erg_line.clear()
        self.erg_line[cmd[2]] = cmd[8]

        self.logger.info("erg {} is lane: {}".format(cmd[2], cmd[8]))
        self.logger.debug(_int2bytes(cmd))

    def set_all_race_params_command(self, cmd):
        if cmd[2] == 0x01:
            self.total_distance = _bytes2int(cmd[30:34])
            self.logger.info("set distance: {}".format(self.total_distance))
            self.logger.debug(_int2bytes(cmd))

            self.init_race_logger()
            self.race_data.clear()
            self.write_config()

    def update_race_data_response(self, resp):
        src = resp[3]
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

        if src == len(self.participant_name):
            self.send_race_data()

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

    def test(self):
        file_with_hex_cmd = "test.txt"
        self.timeout = 0.5
        with open(file_with_hex_cmd, "r") as f:
            for line in f:
                cmd = line[:-1]
                while "f3 00" in cmd:
                    cmd = cmd.replace("f3 00", "f0")
                while "f3 01" in cmd:
                    cmd = cmd.replace("f3 01", "f1")
                while "f3 02" in cmd:
                    cmd = cmd.replace("f3 02", "f2")
                while "f3 03" in cmd:
                    cmd = cmd.replace("f3 03", "f3")

                cmd = [int(i, 16) for i in cmd.split(" ")]
                self.handler(cmd)


if __name__ == "__main__":
    race = PyStrokeSide()
    #race.sniffing()
    race.test()
