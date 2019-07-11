from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace


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

    pySS.master_erg.set_screen_state(destination=0xFF, state=0x01)  # on PM5 state screen "request next Erg #"

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

