from subprocess import Popen, PIPE
import os
from datetime import datetime
import socketio
import logging
import random



class PyStrokeSide:
    file_with_hex_cmd = "test.txt"
    # PATH = r"C:\Program Files\USBPcap"
    _PATH_USBPCAP = os.getcwd() + r"\USBPcap"
    command = _PATH_USBPCAP + r"\USBPcapCMD.exe -d \\.\USBPcap1 -o - -A"
    LEN_BUF = 10

    def __init__(self, address=None, token=None):
        self.race_name = None
        self.erg_line = {}
        self.participant_name = {}
        self.total_distance = None
        self.race_data = []

        self.address = address
        self.token = token
        self.timeout = 0

        if self.address is not None:
            self.sio = socketio.Client()
            self.sio.connect(self.address)
            self.sio.emit('login', {'token': self.token})

        self.logger = self.init_logger()
        self.race_logger = None

    def init_logger(self):
        if "LogData" not in os.listdir():
            os.mkdir("LogData")
        if "Log" not in os.listdir(os.getcwd() + "\\LogData"):
            os.mkdir(os.getcwd() + "\\LogData" + "\\Log")

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)

        path = os.getcwd() + "\\LogData" + "\\Log"
        filehandler = logging.FileHandler(path + "\\{}_{:%Y-%m-%d_%H-%M-%S}.log".format(self.race_name, datetime.now()))
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(filehandler)

        return logger

    def init_race_logger(self):
        race_logger = logging.getLogger(__file__)
        race_logger.setLevel(logging.DEBUG)

        if "RaceLog" not in os.listdir(os.getcwd() + "\\LogData"):
            os.mkdir(os.getcwd() + "\\LogData" + "\\RaceLog")
            self.logger.debug('Create "RaceLog" directory')

        path = os.getcwd() + "\\LogData" + "\\RaceLog"
        rh = logging.FileHandler(path + "\\{}_{:%Y-%m-%d_%H-%M-%S}.log".format(self.race_name, datetime.now()))
        rh.setLevel(logging.INFO)
        race_logger.addHandler(rh)

        self.logger.info("Init Race Log File")
        return race_logger

    @staticmethod
    def __bytes2int(raw_bytes):
        raw_bytes = raw_bytes[::-1]
        num_bytes = len(raw_bytes)
        integer = 0

        for k in range(num_bytes):
            integer = (raw_bytes[k] << (8 * k)) | integer

        return integer

    @staticmethod
    def __bytes2ascii(raw_bytes):
        word = ""
        for letter in raw_bytes:
            word += chr(letter)

        return word

    def send_race_data(self):
        data = {}
        data["timestamps"] = datetime.now().isoformat(sep=" ", timespec='seconds')
        data["race_name"] = self.race_name
        data["total_distance"] = self.total_distance
        data["race_data"] = self.race_data

        if self.address is not None:
            self.sio.emit('send_data', {'data': data})
            # time.sleep(self.timeout)

        self.race_logger.info(data)
        self.logger.debug("Send race data to server: {}".format(data))

    def sniffing(self):
        process = Popen(self.command, stdout=PIPE, shell=True)
        self.logger.info("Open USBPcap")
        buffer = b""

        self.logger.info("Start sniffing")
        while True:
            buffer += process.stdout.read(self.LEN_BUF)
            if b"\x02\xf0" in buffer and b"\xf2" in buffer:
                cmd = buffer[buffer.find(b"\x02\xf0"):buffer.find(b"\xf2") + 1]
                if cmd:
                    self.handler([c for c in cmd])

            buffer = buffer[buffer.find(b"\xf2") + 1:]

    def set_race_participant_command(self, cmd):
        line = cmd[8]
        if cmd[2] == 0x01 and line == 0:  # name race
            self.race_name = self.__bytes2ascii(cmd[9:9 + cmd[7] - 2])
            self.race_logger = self.init_race_logger()
            self.logger.debug("Name race:", self.race_name)
        elif cmd[2] == 0xFF:  # name participant
            self.participant_name[line] = self.__bytes2ascii(cmd[9:9 + cmd[7] - 2])
            self.logger.debug("Participant", line, "have name:", self.participant_name[line])

    def set_race_lane_setup_command(self, cmd):
        self.erg_line[cmd[2]] = cmd[8]
        self.logger.debug("erg", cmd[2], "is lane:", cmd[8])

    def set_all_race_params_command(self, cmd):
        if cmd[2] == 0x01:
            self.total_distance = self.__bytes2int(cmd[30:34])
            self.logger.debug("set distance:", self.total_distance)

    def update_race_data_response(self, resp):
        src = resp[3]
        distance = round(self.__bytes2int(resp[14:18]) * 0.1, 1)  # dist * 10
        time = round(self.__bytes2int(resp[20:24]) * 0.01, 2)  # time * 100
        stroke = resp[24]  # stroke
        split = round(500 * (time / distance) if distance != 0 else 0, 2)
        self.logger.debug(" ".join(["erg", str(src), ": distance -", str(distance)]))
        self.logger.debug(" ".join(["erg", str(src), ": time -", str(time)]))
        self.logger.debug(" ".join(["erg", str(src), ": stroke -", str(stroke)]))
        self.logger.debug(" ".join(["erg", str(src), ": split -", str(split)]))

        self.race_data.append(dict(line=self.erg_line[src],
                                   participant_name=self.participant_name[self.erg_line[src]],
                                   distance=distance,
                                   time=time,
                                   stroke=stroke,
                                   split=split))

        if len(self.race_data) == len(self.erg_line):
            self.send_race_data()
            self.race_data = []

    def handler(self, cmd):
        if cmd[4] == 0x76 and cmd[6] == 0x32:
            self.set_race_participant_command(cmd)
        elif cmd[4] == 0x7e and cmd[6] == 0x0b:
            self.set_race_lane_setup_command(cmd)
        elif cmd[4] == 0x76 and cmd[6] == 0x1d:
            self.set_all_race_params_command(cmd)
        elif cmd[5] == 0x76 and cmd[7] == 0x33:
            self.update_race_data_response(cmd)

    def test(self):
        self.erg_line = {1: 1, 2: 2}
        self.participant_name = {1: "Lane1", 2: "Lane2"}
        with open(self.file_with_hex_cmd, "r") as f:
            for line in f:
                cmd = [int(i, 16) for i in line[:-1].split(" ")]
                self.handler(cmd)
                self.logger.debug(line[:-1])

        self.sio.disconnect()


if __name__ == "__main__":
    ADDRESS = "http://broadcast.strokeside.ru:9090"
    TOKEN = "aeksei"

    race = PyStrokeSide(ADDRESS, TOKEN)
    #race.sniffing()
    race.test()
