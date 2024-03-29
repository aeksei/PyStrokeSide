import json
import logging.config
from pyrow import pyrow
from pyrow.csafe import csafe_dic
from pyrow.csafe.csafe_cmd import __bytes2int, __int2bytes
from pyrow.csafe.csafe_cmd import gen_auth_code, get_time_cmd

bytes2int = __bytes2int
int2bytes = __int2bytes


class PyErgRace(pyrow.PyErg):
    """
    Manages low-level erg communication for race
    """
    _serial_num = None
    _erg_num = 0xFD
    _race_line = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("logging.json", "r") as f:
            logging.config.dictConfig(json.load(f))
        self.pyrow_race_logger = logging.getLogger("pyrow_race")

    def get_erg_num(self):
        return self._erg_num

    def set_erg_num(self, erg_num):
        self._erg_num = erg_num

    def reset_erg_num(self, destination=0xFF):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_reset_erg_num
        :return:
        """
        cmd = 'reset_erg_num'
        data = csafe_dic.cmds[cmd]
        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} for {:02X} erg'.format(self._erg_num, cmd, destination))
        self.send(message)
        self._erg_num = 0xFD

    def get_serial_num(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_get_serial_num
        :return: serial number of erg 430343302
        """
        cmd = 'get_serial_num'
        data = csafe_dic.cmds[cmd]
        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {}'.format(self._erg_num, cmd))
        resp = []
        while not resp:
            resp = self.send(message)
            if resp:
                serial = resp['CSAFE_GETPMCFG_CMD'][2:]
                self.pyrow_race_logger.debug('Erg {:02X} have {} serial num'.format(destination,
                                                                                    bytes2int(serial)))
                return bytes2int(serial)

    def set_erg_num(self, erg_num, serial_num):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_erg_num
        :return:
        """
        cmd = 'set_erg_num'
        data = csafe_dic.cmds[cmd][:-1]
        data.extend(int2bytes(4, serial_num)[::-1])
        data.append(erg_num)

        if self._erg_num == 0xFD:
            self.pyrow_race_logger.debug('Erg {:02X} {} "{:02X}" to erg {}'.format(self._erg_num,
                                                                                   cmd,
                                                                                   erg_num,
                                                                                   serial_num))
            destination = self._erg_num
            self._erg_num = erg_num
        else:
            self.pyrow_race_logger.debug('Erg {:02X} {} "{:02X}" to erg {}'.format(self._erg_num,
                                                                                   cmd,
                                                                                   erg_num,
                                                                                   serial_num))
            destination = 0xFF

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.send(message)

    def get_erg_num_confirm(self, destination, serial_num):
        """
        get_erg_num_confirm
        :param destination:
        :param serial_num:
        :return: confirm set erg num
        """
        cmd = 'get_erg_num_confirm'
        data = csafe_dic.cmds[cmd][:-1]
        data.extend(int2bytes(4, serial_num)[::-1])

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)
        self.pyrow_race_logger.debug('Erg {:02X} {} from erg {} with address {:02X}'.format(self._erg_num,
                                                                                            cmd,
                                                                                            serial_num,
                                                                                            destination))
        resp = self.send(message)
        if 'CSAFE_GETPMCFG_CMD' in resp:
            self.pyrow_race_logger.debug('Erg {} confirm serial number {}'.format(destination, serial_num))
            return True
        else:
            self.pyrow_race_logger.debug('Erg {} don\'t confirm serial number {}'.format(destination, serial_num))
            return False

    def set_screen_state(self, destination, state):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_screen_state@@YAFGEE@Z(guessed Arg1,Arg2,Arg3)

        :return:
        """
        cmd = 'set_screen_state'
        data = csafe_dic.cmds[cmd][:-1]
        data.append(state)

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)
        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X} with state {:02X}'.format(self._erg_num,
                                                                                            cmd,
                                                                                            destination,
                                                                                            state))
        self.send(message)

    def VRPM3Race_100012D0(self, destination):
        """
        VRPM3Race.100012D0(guessed Arg1,Arg2)
        :return:
        """
        cmd = 'VRPM3Race_100012D0'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def call_10001210(self, destination):
        cmd = 'call_10001210'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7F, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def call_10001400(self, destination, serial_num):
        """
        02 f0 01 00 76 0e 1a 0c serial 67 6f 21 cc 19 8c 48 e6 03 f2
        :param destination:
        :param serial_num:
        :return:
        """
        cmd = 'call_10001400'
        data = csafe_dic.cmds[cmd]
        data = data[:-1]
        data.extend(gen_auth_code(serial_num))

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_race_idle_params(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_idle_params@@YAFGGGGG@Z
        02 f0 01 00 76 0a 21 08 ff ff 38 40 00 05 00 01 29 f2
                             08 ff ff 38 40 00 05 00 01 3d 04 00 00 00 00
        :return:
        """
        cmd = 'set_race_idle_params'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_datetime(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_datetime@@YAFGEEEEEG@Z>]
        02 f0 01 00 76 09 22 07 0a 0e 01 0c 01 07 e2 b7 f2
        :return:
        """
        cmd = 'set_datetime'
        data = csafe_dic.cmds[cmd]
        data = data[:-1]
        data.extend(get_time_cmd())

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_screen_error_mode(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_screen_error_mode@@YAFGE@Z>]
        02 F0 01 00 76 03 27 01 00 53 F2
        :return:
        """
        cmd = 'set_screen_error_mode'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_cpu_tick_rate(self, destination, state):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_cpu_tick_rate@@YAFGE@Z
        02 f0 01 00 76 03 25 01 "bar" 50 f2
        :return:
        """
        cmd = 'set_cpu_tick_rate'
        data = csafe_dic.cmds[cmd]
        data[2] = state

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def get_cpu_tick_rate(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_get_cpu_tick_rate@@YAFGPAE@Z
        02 f0 01 00 7e 01 9d e2 f2
        :return:
        """
        cmd = 'get_cpu_tick_rate'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def get_erg_info(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_get_erg_info@@YAFGPAKPAE1111111111PAG@Z(guessed Arg1,Arg2,Arg3,Arg4,Arg5,Arg6,Arg7,Arg8,Arg9,Arg10,Arg11,Arg12,Arg13,Arg14)
        02 f0 01 00 7e 02 98 c9 2d f2
        """
        cmd = 'get_erg_info'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_race_starting_physical_address(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_starting_physical_address@@YAFGE@Z
        :return:
        """
        cmd = 'set_race_starting_physical_address'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_race_operation_type(self, destination, state):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_operation_type@@YAFGE@Z
        :return:
        """
        cmd = 'set_race_operation_type'
        data = csafe_dic.cmds[cmd][:-1]
        # TODO fix this
        if isinstance(state, list):
            data.extend(state)
            state = state[0]
        else:
            data.append(state)

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X} with state {:02X}'.format(self._erg_num,
                                                                                            cmd,
                                                                                            destination,
                                                                                            state))
        self.send(message)

    def get_race_lane_check(self, destination):
        """
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_operation_type@@YAFGE@Z
        02 f0 01 00 7e 01 87 f8 f2
        :return:
        """
        cmd = 'get_race_lane_check'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def get_race_lane_request(self, destination=0xFF, race_line=0x00):
        # TODO check serial num
        """
        1000A2B7
        VRPM3Csafe.?tkcmdsetCSAFE_get_race_lane_request@@YAFGPAE@Z

        02 f0 ff 00 7e 04 51 02 00 ff d6 f2
        :return:
        """
        cmd = 'get_race_lane_request'
        data = csafe_dic.cmds[cmd]
        data[-2] = race_line
        data[-1] = destination

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num,
                                                                          cmd,
                                                                          destination))
        resp = self.send(message)
        if 'CSAFE_GETPMCFG_CMD' in resp:
            erg_num = resp['CSAFE_GETPMCFG_CMD'][2]
            serial = bytes2int(resp['CSAFE_GETPMCFG_CMD'][3:-1])
            if destination != 0xFF:
                self.pyrow_race_logger.debug('For erg {:02X} with {} serial number set {} line number'.format(erg_num,
                                                                                                              serial,
                                                                                                              race_line))
            else:
                self.pyrow_race_logger.debug('Erg {:02X} with {} serial number request line number'.format(erg_num,
                                                                                                           serial))
            return erg_num, serial
        return ()

    def set_race_lane_setup(self, destination, race_line):
        """
        1000A317
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_lane_setup@@YAFGGG@Z
        02 F0 01 00 7E 04 0B 02 + race_line + 00 72 F2
        :return:
        """
        cmd = 'set_race_lane_setup'
        data = csafe_dic.cmds[cmd]
        data[-2] = race_line

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X} with race line {:02X}'.format(self._erg_num,
                                                                                                cmd,
                                                                                                destination,
                                                                                                race_line))
        self.send(message)

    def foo(self, destination):
        """
        02 f0 ff 00 76 07 1b 04 00 00 00 01 d7 b8 f2

        :param destination:
        :return:
        """
        cmd = 'foo'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_workout_type(self, destination, state):
        """
        00BBC668
        VRPM3Csafe.?tkcmdsetCSAFE_set_workout_type@@YAFGE@Z
        02 F0 01 00 76 03 01 01 state 74 F2

        :return:
        """
        cmd = 'set_workout_type'
        data = csafe_dic.cmds[cmd]
        # data[-1] = state

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_race_participant(self, destination, lane_number, name):
        """
        00BBB81F
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_participant@@YAFGGPAD@Z
        02 F0 FF 00 76 09 32 07 02 4C 61 6E 65 32 00 5C F2"  # Lane2 4C 61 6E 65 32
        :return:
        """
        cmd = 'set_race_participant'
        data = csafe_dic.cmds[cmd][:-1]
        hex_name = [ord(c) for c in name]
        hex_name.append(0x00)
        hex_name.insert(0, lane_number)
        hex_name.insert(0, len(hex_name))
        data.extend(hex_name)

        message = [[destination, 0x00, 0x77, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} name: {} to erg with line number {:02X} '.format(self._erg_num,
                                                                                                     cmd,
                                                                                                     name,
                                                                                                     lane_number))
        self.send(message)

    def get_race_participant_count(self, destination):
        """
        00BBBD0F
        VRPM3Csafe.?tkcmdsetCSAFE_get_race_participant_count@@YAFGPAE@Z

        02 F0 02 00 7E 01 96 E9 F2
        :return:
        """
        cmd = 'get_race_participant_count'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        resp = self.send(message)
        count = resp['CSAFE_GETPMCFG_CMD'][2]
        self.pyrow_race_logger.debug('Erg {:02X} have {} setting participant'.format(destination, count))
        return count

    def get_tick_timebase(self, destination):
        """
        1000B635
        VRPM3Csafe.?tkcmdsetCSAFE_get_tick_timebase@@YAFGPAM@Z

        02 F0 01 00 7E 01 83 FC F2

        :return:
        """
        cmd = 'get_tick_timebase'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x7E, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def latch_tick_time(self, destination):
        """
        1000CD4F
        VRPM3Csafe.?tkcmdsetCSAFE_latch_tick_time@@YAFG@Z

        02 F0 01 00 77 01 D7 A1 F2
        :return:
        """

        cmd = 'latch_tick_time'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def get_latched_tick_time(self, destination):
        """
        1000CDC6
        VRPM3Csafe.?tkcmdsetCSAFE_get_latched_tick_time@@YAFGPAM@Z

        02 F0 01 00 7E 01 C4 BB F2

        """
        cmd = 'get_latched_tick_time'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        resp = self.send(message)

        return resp['CSAFE_SETPMCFG_CMD'][-4:]

    def set_race_start_params(self, destination, params):
        """
        1000CFD5
        VRPM3Csafe.?tkcmdsetCSAFE_set_race_start_params@@YAFGEEKKK@Z

        02 F0 01 00 76 10 0D 0E 00 00 00 00 42 A8 00 00 44 9B 00 00 46 78 6E F2
        :return:
        """
        cmd = 'set_race_start_params'
        data = csafe_dic.cmds[cmd]
        data = data[:-1]
        data.extend(params)

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def set_all_race_params(self, destination, distance):
        """
        1000C8B1
        VRPM3Csafe.?tkcmdsetCSAFE_set_all_race_params@@YAFGKKKEEKKE@Z
        02 F0 01 00 1D 04 00 00 00 80 1F 04 00 00 02 00 20 04 00 00 0F 00 01 01 03 03 05 80
                + distance +  05 05 80 00 00 01 F4 09 01 00 D4 F2

        :return:
        """

        cmd = 'set_all_race_params'
        data = csafe_dic.cmds[cmd]
        distance = int2bytes(4, distance)[::-1]
        data = data[:-11] + distance + data[-10:]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def configure_workout(self, destination):
        """
        1000C8E1
        VRPM3Csafe.?tkcmdsetCSAFE_configure_workout@@YAFGE@Z

        02 F0 01 00 76 03 14 01 01 61 F2

        :return:
        """
        cmd = 'configure_workout'
        data = csafe_dic.cmds[cmd]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        self.send(message)

    def update_race_data(self, destination, cmd_data):
        """
        1000DF53
        VRPM3Csafe.?tkcmdsetCSAFE_update_race_data@@YAFGPAUTKCMDSET_PM3_RACE_DATA@@PAUTKCMDSET_OVERALL_RACE_DATA@@@Z

        02 F0 02 00 76 22 33 1D 00 01 00 00 00 00 00 00 00 00 00 00 02 01 00 00 00 00 01 02 00 00 00 00 00 00 00 00 00 C6 BA BC BB F2

        :return:
        """
        # TODO top of user
        cmd = 'update_race_data'
        data = csafe_dic.cmds[cmd]
        data = data[:2] + cmd_data + data[3:]

        message = [[destination, 0x00, 0x76, len(data)]]
        message.extend(data)

        self.pyrow_race_logger.debug('Erg {:02X} {} to erg {:02X}'.format(self._erg_num, cmd, destination))
        resp = self.send(message)
        return resp['CSAFE_SETPMCFG_CMD']
