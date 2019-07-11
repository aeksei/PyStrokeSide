from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace

import time


class MasterSlavePyStrokeSide:
    erg_num = {}

    def __init__(self):
        self.master_erg = PyErgRace(list(pyrow.find())[0])

    def setting_erg(self, destination):
        pySS.master_erg.VRPM3Race_100012D0(destination)
        pySS.master_erg.call_10001210(destination)
        pySS.master_erg.set_race_idle_params(destination)
        pySS.master_erg.set_datetime(destination)

        pySS.master_erg.set_screen_error_mode(destination)
        pySS.master_erg.set_cpu_tick_rate(destination, bar=0x01)
        pySS.master_erg.get_cpu_tick_rate(destination)

    def init_master_erg(self):
        self.master_erg.reset_erg_num()

        serial = self.master_erg.get_serial_num(destination=0xFD)
        self.master_erg.set_erg_num(serial, 0x01)
        self.erg_num[serial] = 0x01

        serial = self.master_erg.get_serial_num(destination=0x01)
        self.master_erg.get_erg_num_confirm(0x01, serial)
        self.setting_erg(destination=0x01)


if __name__ == "__main__":
    pySS = MasterSlavePyStrokeSide()

    # Number ALL ergs
    pySS.master_erg.reset_erg_num()
    pySS.erg_num = {}
    pySS.init_master_erg()

    pySS.master_erg.set_race_starting_physical_address(destination=0x01)
    pySS.master_erg.set_race_operation_type(destination=0x01, state=0x04)

    pySS.master_erg.set_race_starting_physical_address(destination=0xFF)
    pySS.master_erg.set_race_operation_type(destination=0xFF, state=0x04)

    pySS.master_erg.set_screen_state(destination=0xFF, state=0x01)

    while True:
        resp = pySS.master_erg.get_race_lane_request()
        time.sleep(1)


