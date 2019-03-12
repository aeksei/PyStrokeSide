from configobj import ConfigObj

CONFIG_FILE = 'race.conf'


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

        """
    
    def write_config(self):
        self.config.set('SERVER', 'address = ', self.address)
        self.config.set('SERVER', 'token = ', self.token)
    
        self.config.set('RACE', 'total_distance', str(self.total_distance))
        self.config.set('RACE', 'race_name', str(self.race_name))
        self.config.set('RACE', 'race_file', str(self.race_file))
        for erg in self.erg_line:
            self.config.set('NUMERATION_ERG', str(erg), str(self.erg_line[erg]))
        for line in self.participant_name:
            self.config.set('PARTICIPANT_NAME', str(line), str(self.participant_name[line]))
    
        with open(self.CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)
            self.logger.info("write configure")
    
    def restore_config(self):
        if self.CONFIG_FILE not in os.listdir(self.HOME_DIR):
            self.create_config()
        else:
            self.config.read(self.CONFIG_FILE)
    
            try:
                self.address = self.config.get('SERVER', 'address')
            except configparser.NoOptionError:
                self.address = None
            try:
                self.token = self.config.get('SERVER', 'token')
            except configparser.NoOptionError:
                self.token = None
    
            self.race_name = self.config.get('RACE', 'race_name')
            self.total_distance = self.config.get('RACE', 'total_distance')
            self.race_file = self.config.get('RACE', 'race_file')
    
            for erg_num in self.config["NUMERATION_ERG"]:
                self.erg_line[int(erg_num)] = self.config.getint("NUMERATION_ERG", erg_num)
            for line in self.config["PARTICIPANT_NAME"]:
                self.participant_name[int(line)] = self.config.get("PARTICIPANT_NAME", line)
    
            self.logger.info("Restore configure file {}".format(self.CONFIG_FILE))
        """


if __name__ == "__main__":
    conf = Config()
