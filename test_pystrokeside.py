from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace


class MasterSlavePyStrokeSide:

    def __init__(self):
        self.master_erg = PyErgRace(list(pyrow.find())[0])
        self.serial_num = {0x01: [0x19, 0xa6, 0x84, 0x95],
                           0x02: [0x19, 0xa6, 0x84, 0xda]}
        self.race_line = {0x01: 0x01,
                          0x02: 0x02}

    def setting_erg(self, destination):
        self.master_erg.VRPM3Race_100012D0(destination)
        self.master_erg.call_10001210(destination)
        self.master_erg.set_race_idle_params(destination)
        self.master_erg.set_datetime(destination)

        self.master_erg.set_screen_error_mode(destination)
        self.master_erg.set_cpu_tick_rate(destination, bar=0x01)
        self.master_erg.get_cpu_tick_rate(destination)

    def init_master_erg(self):
        self.master_erg.reset_erg_num()

        serial = self.master_erg.get_serial_num(destination=0xFD)
        self.master_erg.set_erg_num(serial, 0x01)
        self.serial_num[0x01] = serial

        serial = self.master_erg.get_serial_num(destination=0x01)
        self.master_erg.get_erg_num_confirm(0x01, serial)

        self.setting_erg(destination=0x01)

    def restore_slave_erg(self):
        for erg_num, serial in self.serial_num.items():
            if erg_num != 0x01:
                self.master_erg.set_erg_num(erg_num, serial)
                self.master_erg.get_erg_num_confirm(erg_num, serial)  # TODO check confirm and miss erg

                self.setting_erg(destination=erg_num)

    def restore_race_line(self):
        for erg_num, serial in self.serial_num.items():
            self.master_erg.get_race_lane_check(destination=erg_num)
            self.master_erg.set_race_lane_setup(destination=erg_num,
                                                race_line=self.race_line[erg_num])
            self.master_erg.get_race_lane_request(destination=erg_num,
                                                  race_line=self.race_line[erg_num])

        self.master_erg.set_screen_state(destination=0xFF, state=0x0e)

    def restore_erg(self):
        self.init_master_erg()
        self.restore_slave_erg()

        self.master_erg.set_race_starting_physical_address(destination=0x01)
        self.master_erg.set_race_operation_type(destination=0x01, state=0x04)

        self.master_erg.set_race_starting_physical_address(destination=0xFF)
        self.master_erg.set_race_operation_type(destination=0xFF, state=0x04)

        self.master_erg.set_screen_state(destination=0xFF, state=0x07)

        self.restore_race_line()


if __name__ == "__main__":
    pySS = MasterSlavePyStrokeSide()
    pySS.restore_erg()

    # Number ALL ergs

    """
    while True:
        resp = pySS.master_erg.get_race_lane_request()
        if 'CSAFE_GETPMCFG_CMD' in resp:
            serial_num = to_hex.list_to_hex_str(resp['CSAFE_GETPMCFG_CMD'][3:-1])
            if serial_num not in race_line:
                race_line[serial_num] = len(race_line) + 1
            if resp['CSAFE_GETPMCFG_CMD'][2] != 0xFD:
                erg_race.set_race_lane_setup(destination=erg_race.id_erg[serial_num], race_line=race_line[serial_num])
                erg_race.set_screen_state(destination=erg_race.id_erg[serial_num], state=0x02)
            else:
                erg_race.set_erg_num(serial_num=serial_num)
                erg_race.VRPM3Race_10001000(destination=erg_race.id_erg[serial_num])  # may be need resp
                erg_race.set_race_idle_params(destination=erg_race.id_erg[serial_num])
                erg_race.set_datetime(destination=erg_race.id_erg[serial_num])

                erg_race.set_race_operation_type(destination=erg_race.id_erg[serial_num])
                erg_race.set_race_lane_setup(destination=erg_race.id_erg[serial_num], race_line=race_line[serial_num])
                erg_race.set_screen_state(destination=erg_race.id_erg[serial_num], state=0x02)
        print(resp)
        print(race_line)
        # make stop search
        if len(race_line) == 2:
            break
    # press "Done numbering"
    """

