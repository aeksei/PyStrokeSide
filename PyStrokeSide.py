import sys
import json
import logging.config
from time import sleep
from pyrow import pyrow
from config import Config
from pyrow.pyrow_race import PyErgRace
from pyrow.pyrow_data import PyErgRaceData
from pyrow.csafe.csafe_cmd import get_start_param


class PyStrokeSide:
    def __init__(self):
        with open("logging.json", "r") as f:
            logging.config.dictConfig(json.load(f))
        self.PySS_logger = logging.getLogger("PySS")

        self.master_erg = None
        self.erg_race = PyErgRaceData()
        self.config = Config()

        self.erg_num_offset = 2

        self.master_erg_serial = self.config['master_erg_serial']
        self.line_number = {}
        self.erg_num = {}
        self.missing_ergs = {}  # may be use for setting erg

        self.race_name = self.config['race_name']
        self.race_participant = self.config['race_participant']

        self.distance = 1000
        self.team_size = 1

    def discovering_erg(self):
        try:
            return PyErgRace(list(pyrow.find()))
        except ValueError:
            self.PySS_logger.critical("Ergs not found")
            return []

    def reset_all_erg(self):  # reset all
        self.PySS_logger.info("Start reset all ergs")
        for i in range(3):
            self.master_erg.reset_erg_num()
            self.master_erg.set_erg_num(0x01, self.master_erg.get_serial_num(0xFD))

    def setting_erg(self, destination, serial):
        self.PySS_logger.info("Setting erg {:02X} with serial number {}".format(destination, serial))
        self.master_erg.VRPM3Race_100012D0(destination)
        self.master_erg.call_10001210(destination)
        self.master_erg.call_10001400(destination, serial)
        self.master_erg.set_datetime(destination)
        self.master_erg.set_race_idle_params(destination)  # TODO check param

        self.master_erg.set_screen_error_mode(destination)
        self.master_erg.set_cpu_tick_rate(destination, 0x01)
        self.master_erg.get_cpu_tick_rate(destination)

    def restore_master_erg(self):
        self.PySS_logger.info("Start restore master erg")
        is_restore = False
        serial = self.master_erg.get_serial_num(0x01)

        if serial in self.line_number:
            if serial == self.master_erg_serial:
                is_restore = True
                self.PySS_logger.debug('Master erg with serial number {}'
                                       ' was restored from last configuration'.format(self.master_erg_serial))
            else:
                self.PySS_logger.debug('Master erg with serial number {} wasn\'t '
                                       'restored from last configuration'.format(self.master_erg_serial))

                line = self.line_number.pop(serial)
                self.missing_ergs = self.line_number.copy()
                self.line_number.clear()
                self.line_number[serial] = line

        else:
            self.PySS_logger.debug('Master erg with new serial number {} '.format(serial))
            self.line_number[serial] = 0x01

        self.master_erg_serial = serial
        self.config['master_erg_serial'] = self.master_erg_serial
        self.erg_num.clear()
        self.erg_num[self.line_number[self.master_erg_serial]] = 0x01
        self.master_erg.get_erg_num_confirm(0x01, self.master_erg_serial)
        self.setting_erg(0x01, self.master_erg_serial)

        self.PySS_logger.debug('Line number: {}'.format(self.line_number))
        self.PySS_logger.debug('Erg number: {}'.format(self.erg_num))

        return is_restore

    def restore_slave_erg(self):
        self.PySS_logger.info("Start restore slave ergs")
        for serial, line_number in self.line_number.items():
            if serial != self.master_erg_serial:
                erg_num = len(self.erg_num) + 1
                self.erg_num[line_number] = erg_num
                self.master_erg.set_erg_num(erg_num, serial)
                is_restore = self.master_erg.get_erg_num_confirm(erg_num, serial)  # TODO check confirm and miss erg
                if is_restore:
                    self.PySS_logger.debug('Erg {} with serial number {}'
                                           ' was restored from last configuration'.format(erg_num, serial))
                else:
                    self.missing_ergs[serial] = line_number
                    self.PySS_logger.debug('Erg {} with serial number {} wasn\'t '
                                           'restored from last configuration'.format(erg_num, serial))
                self.setting_erg(erg_num, serial)

        self.PySS_logger.debug('Line number: {}'.format(self.line_number))
        self.PySS_logger.debug('Erg number: {}'.format(self.erg_num))

        return self.missing_ergs

    def restore_line_number(self):
        self.PySS_logger.info("Start restore line numbers")
        for line_number, erg_num in self.erg_num.items():
            self.master_erg.get_race_lane_check(erg_num)
            self.master_erg.set_race_lane_setup(erg_num, line_number)
            self.master_erg.get_race_lane_request(erg_num, line_number)

        self.master_erg.set_screen_state(0xFF, 0x0e)

    def restore_erg(self):
        self.PySS_logger.info("Start restore ergs")
        self.reset_all_erg()
        self.missing_ergs.clear()

        self.line_number = self.config['line_number']
        self.PySS_logger.debug('Line number from config: {}'.format(self.line_number))
        self.PySS_logger.debug('Erg number: {}'.format(self.erg_num))

        is_restore = self.restore_master_erg()
        if is_restore:
            self.restore_slave_erg()

        if self.missing_ergs:
            for serial, line_number in self.missing_ergs.items():
                self.PySS_logger.debug('Missing erg with serial num {} '
                                       'on line number {} from last configuration'.format(serial, line_number))

        self.master_erg.set_race_operation_type(0x01, 0x04)
        self.master_erg.set_race_starting_physical_address(0x01)

        self.master_erg.set_race_starting_physical_address(0xFF)
        self.master_erg.set_race_operation_type(0xFF, 0x04)

        self.master_erg.set_screen_state(0xFF, 0x07)

        self.restore_line_number()
        self.master_erg.set_screen_state(0xFF, 0x0E)

    def request_new_line_number(self):
        resp = self.master_erg.get_race_lane_request()
        if resp:
            erg_num = resp[0]
            serial = resp[1]

            if erg_num == 0xFD:
                erg_num = len(self.erg_num) + self.erg_num_offset  # ToDo may be make check min(erg_num)
                self.master_erg.set_erg_num(erg_num, serial)  # set new erg_num
                self.master_erg.get_erg_num_confirm(erg_num, serial)
                self.setting_erg(erg_num, serial)
                self.master_erg.set_race_operation_type(erg_num, 0x04)
            else:
                self.erg_num_offset = 1

            line_number = len(self.line_number) + 1
            self.line_number[serial] = line_number
            self.erg_num[line_number] = erg_num

            self.master_erg.set_race_lane_setup(erg_num, line_number)
            self.master_erg.set_screen_state(erg_num, 0x02)
            self.master_erg.get_race_lane_request(erg_num, line_number)

            self.PySS_logger.debug('Line number: {}'.format(self.line_number))
            self.PySS_logger.debug('Erg number: {}'.format(self.erg_num))

    def number_all_erg(self):
        self.PySS_logger.info("Start number all ergs")
        self.line_number.clear()
        self.erg_num.clear()
        self.missing_ergs.clear()
        self.erg_num_offset = 2

        self.reset_all_erg()

        self.master_erg.set_race_starting_physical_address(0x01)
        self.master_erg.set_race_operation_type(0x01, 0x04)
        self.master_erg.set_race_starting_physical_address(0xFF)
        self.master_erg.set_race_operation_type(0xFF, 0x04)
        self.master_erg.set_screen_state(0xFF, 0x01)

        try:
            while True:  # ToDo may me make missing_erg function
                self.request_new_line_number()

        except KeyboardInterrupt:
            # press "Done numbering"
            self.PySS_logger.debug('Save to config line number: {}'.format(self.line_number))
            self.config['line_number'] = self.line_number

    def set_race_name(self):
        self.PySS_logger.info("Set race name")
        for erg_num in self.erg_num:
            self.master_erg.set_race_participant(erg_num, 0x00, self.race_name)

    def set_participant_name(self):
        self.PySS_logger.info("Start set participant name")
        # TODO by participant name
        for erg_num, erg_line in self.erg_num.items():
            self.master_erg.set_race_participant(0xFF, erg_line, self.race_participant[erg_num])

        self.PySS_logger.info("Start check participant name for each erg")
        for check_erg_num in self.erg_num:
            count_participant = self.master_erg.get_race_participant_count(check_erg_num)
            if count_participant != len(self.race_participant):
                for erg_num, erg_line in self.erg_num.items():
                    self.master_erg.set_race_participant(check_erg_num, erg_line, self.race_participant[erg_num])

    def set_race(self):
        self.PySS_logger.info("Start set race")
        # TODO by participant name
        for erg_num in self.erg_num:
            self.master_erg.set_screen_state(erg_num, 0x08)
        for erg_num in self.erg_num:
            self.master_erg.set_race_operation_type(erg_num, 0x06)

        self.set_race_name()
        self.set_participant_name()

        for erg_num in self.erg_num:
            self.master_erg.set_screen_state(erg_num, 0x27)
        # TODO CSAFE_SETCALORIES_CMD
        for erg_num in self.erg_num:
            self.master_erg.set_screen_state(erg_num, 0x1f)
        for erg_num in self.erg_num:
            self.master_erg.set_workout_type(erg_num, 0x00)
            self.master_erg.set_screen_state(erg_num, 0x03)
        for erg_num in self.erg_num:
            self.master_erg.set_race_operation_type(erg_num, 0x0C)

    def prepare_to_race(self):
        self.PySS_logger.info("Prepare to race")
        for erg_num in self.erg_num:
            self.master_erg.set_race_operation_type(erg_num, [0x06, 0x9d, 0x83])
        for erg_num in self.erg_num:
            self.master_erg.set_cpu_tick_rate(erg_num, 0x02)
        for erg_num in self.erg_num:
            self.master_erg.set_race_operation_type(erg_num, 0x07)
        self.master_erg.foo(0xff)
        for erg_num in self.erg_num:
            self.master_erg.latch_tick_time(erg_num)
        for erg_num in self.erg_num:
            self.master_erg.set_race_operation_type(erg_num, 0x06)
        for erg_num in self.erg_num:
            self.master_erg.set_all_race_params(erg_num, self.distance)
            self.master_erg.configure_workout(erg_num)
            self.master_erg.set_screen_state(erg_num, 0x04)
        for erg_num in self.erg_num:
            self.master_erg.set_race_operation_type(erg_num, 0x08)

        self.erg_race.set_config_race(len(self.erg_num), self.team_size, self.distance)

    def start_race(self):
        self.PySS_logger.info("Start race")
        # latch_time = self.master_erg.get_latched_tick_time(0x01)  # as in erg_race
        # TODO check_flywheels_moving
        for erg_num in self.erg_num:
            self.master_erg.get_erg_info(erg_num)

        latch_time = self.master_erg.get_latched_tick_time(0x01)
        params = get_start_param(latch_time)
        for erg_num in self.erg_num:
            self.master_erg.set_race_start_params(erg_num, params)
            self.master_erg.set_race_operation_type(erg_num, 0x09)

        self.wait(3)  # TODO check false start

    def process_race_data(self):
        self.PySS_logger.info("Race data from ergs")
        try:
            while True:
                for erg_num, line_number in self.erg_num.items():
                    cmd_data = self.erg_race.get_update_race_data(line_number)
                    resp = self.master_erg.update_race_data(erg_num, cmd_data)
                    self.erg_race.set_update_race_data(line_number, resp)
                sleep(1)  # ToDO sleep time
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            self.close()

    def close(self):
        self.PySS_logger.info("Close race")
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
                for erg_num in self.erg_num:
                    self.master_erg.get_erg_info(erg_num)
                sleep(1)
        else:
            try:
                while True:
                    for erg_num in self.erg_num:
                        self.master_erg.get_erg_info(erg_num)
                    sleep(1)
            except KeyboardInterrupt:
                pass


class PyStrokeSideConsole:
    def __init__(self):
        self.pySS = PyStrokeSide()
        self.ergs = self.pySS.discovering_erg()

        self.cmd = {}

    def run(self):
        if self.ergs:
            self.pySS.master_erg = self.ergs[0]
            self.pySS.restore_erg()
            self.pySS.wait(5)
        else:
            self.write({'erg_numeration': {'Not found ergs': ''}})

        # move to up condition
        while True:
            if self.read():
                break

    def read(self):
        line = sys.stdin.readline()
        if line:
            self.cmd = json.loads(line[:-1])
            self.pySS.PySS_logger.debug("receive {}".format(self.cmd))
        else:
            return {}
        sys.stdin.flush()

    def write(self, cmd):
        self.pySS.PySS_logger.debug("send to server {}".format(cmd))
        cmd = json.dumps(cmd) + '\n'
        sys.stdout.write(cmd)
        sys.stdout.flush()

    def handler(self):
        if 'erg_numeration' in self.cmd:
            if 'number_all_ergs' in self.cmd['erg_numeration']:
                self.pySS.number_all_erg()
                self.cmd = {'erg_numeration': {'request_new_line_number': ''}}
            elif 'request_new_line_number' in self.cmd['erg_numeration']:
                self.pySS.request_new_line_number()
            elif 'number_erg_done' in self.cmd['erg_numeration']:
                self.pySS.PySS_logger.debug('Save to config line number: {}'.format(self.pySS.line_number))
                self.pySS.config['line_number'] = self.pySS.line_number
                self.cmd = {}
            elif 'number_missing_ergs' in self.cmd['erg_numeration']:
                pass


if __name__ == '__main__':

    console = PyStrokeSideConsole()
    console.run()



    """
    pySS.set_race()
    pySS.wait(5)

    pySS.prepare_to_race()
    pySS.wait(10)

    pySS.start_race()

    pySS.process_race_data()

    pySS.wait(5)
    pySS.close()
    """



