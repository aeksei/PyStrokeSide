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
            self.restore()

    def __setitem__(self, key, value):
        self.data[key] = value
        self.write()

    def __getitem__(self, item):
        return self.data[item]

    def create(self):
        self['line_number'] = {}
        self['master_erg_serial'] = 430343302

        self['race_name'] = "test_race"
        self['race_participant'] = {0x01: "Lane_1",
                                    0x02: "Lane_2"}
        self.write()

    def write(self):
        with open(self.filename, "w") as write_file:
            json.dump(self.data, write_file, indent=4)

    def restore(self):
        with open(self.filename, "r") as read_file:
            self.data = json.load(read_file, object_hook=self.keystoint)

    def keystoint(self, d):
        return {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()}


if __name__ == "__main__":
    config = Config()
    print(config['line_number'])
