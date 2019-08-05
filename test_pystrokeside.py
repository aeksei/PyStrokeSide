from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace
from time import sleep
from pyrow.csafe.csafe_cmd import get_start_param
from config import Config


class MasterSlavePyStrokeSide:

    def __init__(self):
        self.master_erg = PyErgRace(list(pyrow.find())[0])
        self.config = Config()

        self.serial_num = self.config['serial_num']
        self.race_line = self.config['race_line']
        self.missing_ergs = []  # may be use for setting erg

        self.race_name = self.config['race_name']
        self.race_participant = self.config['race_participant']

    def reset_all_erg(self):  # reset all
        for i in range(3):
            self.master_erg.reset_erg_num()
            self.master_erg.set_erg_num(0x01, self.master_erg.get_serial_num(0xFD))

        serial = self.master_erg.get_serial_num(0x01)
        if 0x01 not in self.serial_num:  # number_all_erg
            self.serial_num[0x01] = serial
        elif serial != self.serial_num[0x01]:  # change cable on master_erg
            self.serial_num.clear()
            self.race_line.clear()
            self.serial_num[0x01] = serial

        self.master_erg.get_erg_num_confirm(0x01, self.serial_num[0x01])

    def setting_erg(self, destination, serial):
        self.master_erg.VRPM3Race_100012D0(destination)
        self.master_erg.call_10001210(destination)
        self.master_erg.call_10001400(destination, serial)
        self.master_erg.set_datetime(destination)
        self.master_erg.set_race_idle_params(destination)  # TODO check param

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
        if not self.race_line:
            self.race_line[0x01] = 0x01
        for erg_num, race_line in self.race_line.items():
            self.master_erg.get_race_lane_check(erg_num)
            self.master_erg.set_race_lane_setup(erg_num, race_line)
            self.master_erg.get_race_lane_request(erg_num, race_line)

        self.master_erg.set_screen_state(0xFF, 0x0e)

    def restore_erg(self):
        self.reset_all_erg()
        self.setting_erg(0x01, self.serial_num[0x01])
        self.restore_slave_erg()

        self.master_erg.set_race_operation_type(0x01, 0x04)
        self.master_erg.set_race_starting_physical_address(0x01)

        self.master_erg.set_race_starting_physical_address(0xFF)
        self.master_erg.set_race_operation_type(0xFF, 0x04)

        self.master_erg.set_screen_state(0xFF, 0x07)
        self.restore_race_line()

        self.master_erg.set_screen_state(0xFF, 0x0E)

    def number_all_erg(self):
        self.serial_num.clear()
        self.race_line.clear()
        self.reset_all_erg()

        self.master_erg.set_race_starting_physical_address(0x01)
        self.master_erg.set_race_operation_type(0x01, 0x04)

        self.master_erg.set_race_starting_physical_address(0xFF)
        self.master_erg.set_race_operation_type(0xFF, 0x04)

        self.master_erg.set_screen_state(0xFF, 0x01)

        while True:
            resp = pySS.master_erg.get_race_lane_request()
            if resp:
                erg_num = resp[0]
                serial = resp[1]

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
            if len(self.race_line) == 3:
                self.config['serial_num'] = self.serial_num
                self.config['race_line'] = self.race_line
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

    def prepare_to_race(self):
        for erg_num in self.race_line:
            self.master_erg.set_race_operation_type(erg_num, [0x06, 0x9d, 0x83])

        for erg_num in self.race_line:
            self.master_erg.set_cpu_tick_rate(erg_num, 0x02)

        for erg_num in self.race_line:
            self.master_erg.set_race_operation_type(erg_num, 0x07)

        self.master_erg.foo(0xff)

        for erg_num in self.race_line:
            self.master_erg.latch_tick_time(erg_num)

        for erg_num in self.race_line:
            self.master_erg.set_race_operation_type(erg_num, 0x06)

        for erg_num in self.race_line:
            self.master_erg.set_all_race_params(erg_num, 2000)
            self.master_erg.configure_workout(erg_num)
            self.master_erg.set_screen_state(erg_num, 0x04)

        for erg_num in self.race_line:
            self.master_erg.set_race_operation_type(erg_num, 0x08)

    def start_race(self):
        latch_time = self.master_erg.get_latched_tick_time(0x01)
        # TODO check_flywheels_moving
        for erg_num in self.race_line:
            self.master_erg.get_erg_info(erg_num)

        params = get_start_param(latch_time)
        for erg_num in self.race_line:
            self.master_erg.set_race_start_params(erg_num, params)
            self.master_erg.set_race_operation_type(erg_num, 0x09)

        # may be 3 times
        pySS.wait(4)

    def process_race_data(self):
        for i in range(100):
            for erg_num in self.race_line:
                self.master_erg.update_race_data(erg_num)

    def close(self):
        self.master_erg.set_race_operation_type(0x01, 0x06)
        self.master_erg.set_screen_state(0xFF, 0x06)
        sleep(0.5)

        self.master_erg.set_race_operation_type(0xFF, 0x06)
        self.master_erg.set_screen_state(0xFF, 0x15)
        sleep(0.5)

        self.master_erg.set_screen_state(0xFF, 0x27)
        self.master_erg.set_race_operation_type(0xFF, 0x00)

    def wait(self, time=0):
        if time:
            for _ in range(time):
                for erg_num in self.race_line:
                    self.master_erg.get_erg_info(erg_num)
                sleep(1)
        else:
            while True:
                for erg_num in self.race_line:
                    self.master_erg.get_erg_info(erg_num)
                sleep(1)


if __name__ == "__main__":
    pySS = MasterSlavePyStrokeSide()
    print('restore_erg')
    pySS.restore_erg()
    pySS.wait(3)

    # print('number_all_erg')
    pySS.number_all_erg()
    # print('restore_erg')
    pySS.restore_erg()
    sleep(5)

    """
    print('set race')
    pySS.set_race()
    pySS.wait(5)

    print('prepare to race')
    pySS.prepare_to_race()
    pySS.wait(10)

    pySS.start_race()

    pySS.process_race_data()
    """
    print('close')
    pySS.close()

