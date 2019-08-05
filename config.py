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
            self.read()

    def __setitem__(self, key, value):
        self.data.update((key, value))
        self.write()

    def __getitem__(self, item):
        return self.data[item]

    def create(self):
        self['serial_num'] = {0x01: 430343317,
                              0x02: 430343386}
        self['race_line'] = {0x01: 0x01,
                             0x02: 0x02}

        self['race_name'] = "test_race"
        self['race_participant'] = {0x01: "Lane_1",
                                    0x02: "Lane_2"}
        self.write()

    def write(self):
        with open(self.filename, "w") as write_file:
            json.dump(self.data, write_file, indent=4)

    def read(self):
        with open(self.filename, "r") as read_file:
            self.data = json.load(read_file, object_pairs_hook=self.keystoint)

    def keystoint(self, x):
        for key, value in x:
            if key.isnumeric():
                return {int(k): v for k, v in x}
            else:
                return x


if __name__ == "__main__":
    config = Config()
    config['serial_num'] = {0x01: 123, 0x02: 456}
    print(config.data)
