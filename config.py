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

    def create(self):
        self['SERVER'] = {}
        self['SERVER']['address'] = ''
        self['SERVER']['token'] = ''

        self['RACE'] = {}
        self['RACE']['total_distance'] = ''
        self['RACE']['race_name'] = ''
        self['RACE']['race_file'] = ''

        self['NUMERATION_ERG'] = {}

        self['PARTICIPANT_NAME'] = {}

        self.write()


if __name__ == "__main__":
    conf = Config()
