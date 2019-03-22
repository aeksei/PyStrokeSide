import os
from configobj import ConfigObj

CONFIG_FILE = 'race.conf'


def _bytes2int(raw_bytes):
    raw_bytes = raw_bytes[::-1]
    num_bytes = len(raw_bytes)
    integer = 0

    for k in range(num_bytes):
        integer = (raw_bytes[k] << (8 * k)) | integer

    return integer


def _bytes2ascii(raw_bytes):
    word = ""
    for letter in raw_bytes:
        word += chr(letter)

    return word


def _int2bytes(int_list):
    return " ".join([hex(i)[2:].rjust(2, "0") for i in int_list])


class Config(ConfigObj):
    def __init__(self, config_file=CONFIG_FILE):
        super().__init__(config_file, write_empty_values=True)

        self.address = ''
        self.token = ''

        self.total_distance = ''
        self.race_name = ''
        self.race_file = ''
        self.race_team = 1

        self.erg_line = {}

        self.participant_name = {}

        self.HOME_DIR = os.getcwd()
        if self.filename not in os.listdir(self.HOME_DIR):
            self.create()
        else:
            self.restore()

    def create(self):
        self['SERVER'] = {}
        self['SERVER']['address'] = self.address
        self['SERVER']['token'] = self.token

        self['RACE'] = {}
        self['RACE']['total_distance'] = self.total_distance
        self['RACE']['race_name'] = self.race_name
        self['RACE']['race_file'] = self.race_file
        self['RACE']['race_team'] = self.race_team

        self['NUMERATION_ERG'] = {}

        self['PARTICIPANT_NAME'] = {}

        self.write()
        self.restore()

    def restore(self):
        if 'address' in self['SERVER']:
            self.address = self['SERVER']['address'] if self['SERVER']['address'] != '' else None
        else:
            self.address = None
        if 'token' in self['SERVER']:
            self.token = self['SERVER']['token'] if self['SERVER']['token'] != '' else None
        else:
            self.token = None

        self.total_distance = self['RACE']['total_distance'] if self['RACE']['total_distance'] != '' else None
        self.race_name = self['RACE']['race_name'] if self['RACE']['race_name'] != '' else None
        self.race_file = self['RACE']['race_file'] if self['RACE']['race_file'] != '' else None
        self.race_team = self['RACE'].as_int('race_team')

        for erg_num in self['NUMERATION_ERG']:
            self.erg_line[int(erg_num)] = self['NUMERATION_ERG'].as_int(erg_num)
        for line in self["PARTICIPANT_NAME"]:
            self.participant_name[int(line)] = self["PARTICIPANT_NAME"][line]


if __name__ == "__main__":
    conf = Config()
