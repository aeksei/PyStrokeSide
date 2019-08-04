import os
import json

CONFIG_FILE = 'conf.json'

class Config:
    def __init__(self, config_file=CONFIG_FILE):
        self.HOME_DIR = os.getcwd()
        self.filename = config_file
        self.data = {}

        if self.filename not in os.listdir(self.HOME_DIR):
            self.create()
        else:
            self.read(self.filename)

        self.address = ''
        self.token = ''

        self.total_distance = ''
        self.race_name = ''
        self.race_file = ''
        self.race_team = 1

        self.erg_line = {}

        self.participant_name = {}

    def create(self):
        self.data['serial_num'] = {0x01: [0x19, 0xa6, 0x84, 0x95],
                                   0x02: [0x19, 0xa6, 0x84, 0xda]}
        self.write()

    def write(self):
        with open(self.filename, "w") as write_file:
            json.dump(self.data, write_file, indent=4)


if __name__ == "__main__":
    config = Config()
