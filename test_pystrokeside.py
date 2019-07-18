from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace
from time import sleep


class MasterSlavePyStrokeSide:

    def __init__(self):
        self.master_erg = PyErgRace(list(pyrow.find())[0])
        self.serial_num = {0x01: [0x19, 0xa6, 0x84, 0x95],
                           0x02: [0x19, 0xa6, 0x84, 0xda]}
        self.race_line = {0x01: 0x01,
                          0x02: 0x02}

        self.race_name = "test_race"
        self.race_participant = {0x01: "Lane_1",
                                 0x02: "Lane_2"}

    def reset_all_erg(self):  # reset all
        self.master_erg.reset_erg_num()

        serial = self.master_erg.get_serial_num(0xFD)
        erg_num = 0x01
        self.serial_num[erg_num] = serial
        self.master_erg.set_erg_num(erg_num, serial)

        serial = self.master_erg.get_serial_num(erg_num)
        self.master_erg.get_erg_num_confirm(erg_num, serial)

    def setting_erg(self, destination, serial):
        self.master_erg.VRPM3Race_100012D0(destination)
        self.master_erg.call_10001210(destination)
        self.master_erg.call_10001400(destination, serial)
        self.master_erg.set_datetime(destination)
        self.master_erg.set_race_idle_params(destination)

        self.master_erg.set_screen_error_mode(destination)
        self.master_erg.set_cpu_tick_rate(destination, 0x01)
        self.master_erg.get_cpu_tick_rate(destination)

    def restore_slave_erg(self):
        for erg_num, serial in self.serial_num.items():
            if erg_num != 0x01:
                self.master_erg.set_erg_num(erg_num, serial)
                self.master_erg.get_erg_num_confirm(erg_num, serial)  # TODO check confirm and miss erg
                self.setting_erg(erg_num, serial)

    def restore_race_line(self):
        for erg_num, serial in self.serial_num.items():
            self.master_erg.get_race_lane_check(erg_num)
            self.master_erg.set_race_lane_setup(erg_num, self.race_line[erg_num])
            #sleep(0.25)  # need for correct race_lane setup
            self.master_erg.get_race_lane_request(erg_num, self.race_line[erg_num])

        self.master_erg.set_screen_state(0xFF, 0x0e)

    def restore_erg(self):
        self.reset_all_erg()
        self.setting_erg(0x01, self.serial_num[0x01])
        self.restore_slave_erg()

        self.master_erg.set_race_starting_physical_address(0x01)
        self.master_erg.set_race_operation_type(0x01, 0x04)
        self.master_erg.set_race_starting_physical_address(0xFF)
        self.master_erg.set_race_operation_type(0xFF, 0x04)

        self.master_erg.set_screen_state(0xFF, 0x07)
        self.restore_race_line()

    def number_all_erg(self):
        self.serial_num = {}
        self.race_line = {}
        self.reset_all_erg()

        self.master_erg.set_race_starting_physical_address(0x01)
        self.master_erg.set_race_operation_type(0x01, 0x04)

        self.master_erg.set_race_starting_physical_address(0xFF)
        self.master_erg.set_race_operation_type(0xFF, 0x04)

        self.master_erg.set_screen_state(0xFF, 0x01)

        while True:
            resp = pySS.master_erg.get_race_lane_request()
            if 'CSAFE_GETPMCFG_CMD' in resp:
                erg_num = resp['CSAFE_GETPMCFG_CMD'][2]
                serial = resp['CSAFE_GETPMCFG_CMD'][3:-1]

                if erg_num == 0xFD:
                    erg_num = len(self.serial_num) + 1
                    self.serial_num[erg_num] = serial  # new erg num for erg lane request
                    self.master_erg.set_erg_num(erg_num, serial)  # set new erg_num

                    self.master_erg.get_erg_num_confirm(erg_num, serial)
                    self.setting_erg(erg_num, serial)
                    self.master_erg.set_race_operation_type(erg_num, 0x04)

                self.race_line[erg_num] = len(self.race_line) + 1
                self.master_erg.set_race_lane_setup(erg_num, self.race_line[erg_num])
                self.master_erg.set_screen_state(erg_num, 0x02)
                self.master_erg.get_race_lane_request(erg_num, self.race_line[erg_num])

            # make stop search
            if len(self.race_line) == 2:
                break
        # press "Done numbering"

    def set_race_name(self):
        for erg_num in self.race_line:
            self.master_erg.set_race_participant(erg_num, 0x00, self.race_name)

    def set_participant_name(self):
        for erg_num, erg_line in self.race_line.items():
            self.master_erg.set_race_participant(0xFF, erg_line, self.race_participant[erg_num])

        for check_erg_num in self.race_line:
            count_participant = self.master_erg.get_race_participant_count(check_erg_num)
            if count_participant != len(self.race_participant):
                for erg_num, erg_line in self.race_line.items():
                    self.master_erg.set_race_participant(check_erg_num, erg_line, self.race_participant[erg_num])

    def set_race(self):
        for erg_num in self.race_line:
            self.master_erg.set_screen_state(erg_num, 0x08)

        for erg_num in self.race_line:
            self.master_erg.set_race_operation_type(erg_num, 0x06)

        self.set_race_name()
        self.set_participant_name()

        for erg_num in self.race_line:
            self.master_erg.set_screen_state(erg_num, 0x27)

        # TODO CSAFE_SETCALORIES_CMD

        for erg_num in self.race_line:
            self.master_erg.set_screen_state(erg_num, 0x1f)

        for erg_num in self.race_line:
            self.master_erg.set_workout_type(erg_num, 0x00)
            self.master_erg.set_screen_state(erg_num, 0x03)

        for erg_num in self.race_line:
            self.master_erg.set_race_operation_type(erg_num, 0x0C)

    def close(self):
        self.master_erg.set_race_operation_type(0x01, 0x06)
        self.master_erg.set_screen_state(0xFF, 0x06)
        sleep(0.5)

        self.master_erg.set_race_operation_type(0xFF, 0x06)
        self.master_erg.set_screen_state(0xFF, 0x15)
        sleep(0.5)

        self.master_erg.set_screen_state(0xFF, 0x27)
        self.master_erg.set_race_operation_type(0xFF, 0x00)


if __name__ == "__main__":
    pySS = MasterSlavePyStrokeSide()
    pySS.restore_erg()
    sleep(3)

    pySS.number_all_erg()
    sleep(5)

    pySS.set_race()
    sleep(5)

    pySS.close()

