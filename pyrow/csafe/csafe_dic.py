#!/usr/bin/env python
# Copyright (c) 2011 Sam Gambrell
# Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

# Unique Frame Flags
Extended_Frame_Start_Flag = 0xF0
Standard_Frame_Start_Flag = 0xF1
Stop_Frame_Flag = 0xF2
Byte_Stuffing_Flag = 0xF3

# cmds['COMMAND_NAME'] = [0xCmd_Id, [Bytes, ...]]

cmds = {}

# Short Commands
cmds['CSAFE_GETSTATUS_CMD'] = [0x80, []]
cmds['CSAFE_RESET_CMD'] = [0x81, []]
cmds['CSAFE_GOIDLE_CMD'] = [0x82, []]
cmds['CSAFE_GOHAVEID_CMD'] = [0x83, []]
cmds['CSAFE_GOINUSE_CMD'] = [0x85, []]
cmds['CSAFE_GOFINISHED_CMD'] = [0x86, []]
cmds['CSAFE_GOREADY_CMD'] = [0x87, []]
cmds['CSAFE_BADID_CMD'] = [0x88, []]
cmds['CSAFE_GETVERSION_CMD'] = [0x91, []]
cmds['CSAFE_GETID_CMD'] = [0x92, []]
cmds['CSAFE_GETUNITS_CMD'] = [0x93, []]
cmds['CSAFE_GETSERIAL_CMD'] = [0x94, []]
cmds['CSAFE_GETODOMETER_CMD'] = [0x9B, []]
cmds['CSAFE_GETERRORCODE_CMD'] = [0x9C, []]
cmds['CSAFE_GETTWORK_CMD'] = [0xA0, []]
cmds['CSAFE_GETHORIZONTAL_CMD'] = [0xA1, []]
cmds['CSAFE_GETCALORIES_CMD'] = [0xA3, []]
cmds['CSAFE_GETPROGRAM_CMD'] = [0xA4, []]
cmds['CSAFE_GETPACE_CMD'] = [0xA6, []]
cmds['CSAFE_GETCADENCE_CMD'] = [0xA7, []]
cmds['CSAFE_GETUSERINFO_CMD'] = [0xAB, []]
cmds['CSAFE_GETHRCUR_CMD'] = [0xB0, []]
cmds['CSAFE_GETPOWER_CMD'] = [0xB4, []]

# Long Commands
cmds['CSAFE_AUTOUPLOAD_CMD'] = [0x01, [1, ]]  # Configuration (no affect)
cmds['CSAFE_IDDIGITS_CMD'] = [0x10, [1, ]]  # Number of Digits
cmds['CSAFE_SETTIME_CMD'] = [0x11, [1, 1, 1]]  # Hour, Minute, Seconds
cmds['CSAFE_SETDATE_CMD'] = [0x12, [1, 1, 1]]  # Year, Month, Day
cmds['CSAFE_SETTIMEOUT_CMD'] = [0x13, [1, ]]  # State Timeout
cmds['CSAFE_SETUSERCFG1_CMD'] = [0x1A, [0, ]]  # PM3 Specific Command (length computed)
cmds['CSAFE_SETTWORK_CMD'] = [0x20, [1, 1, 1]]  # Hour, Minute, Seconds
cmds['CSAFE_SETHORIZONTAL_CMD'] = [0x21, [2, 1]]  # Distance, Units
cmds['CSAFE_SETCALORIES_CMD'] = [0x23, [2, ]]  # Total Calories
cmds['CSAFE_SETPROGRAM_CMD'] = [0x24, [1, 1]]  # Workout ID, N/A
cmds['CSAFE_SETPOWER_CMD'] = [0x34, [2, 1]]  # Stroke Watts, Units
cmds['CSAFE_GETCAPS_CMD'] = [0x70, [1, ]]  # Capability Code

# Extended Long command
cmds['CSAFE_SETPMCFG_CMD'] = [0x76, []]
cmds['CSAFE_GETPMCFG_CMD'] = [0x7e, []]
cmds['CSAFE_SETPMTIME_CMD'] = [0x77, []]

cmds['reset_erg_num'] = [0xe1, 0x0b, 0x02, 0x00, 0x00]
cmds['get_serial_num'] = [0x82]
cmds['set_erg_num'] = [0x10, 0x05, [4, 1]]  # serial_num, new address
cmds['get_erg_num_confirm'] = [0x50, 0x04, [4, ]]  # add serial_num
cmds['set_screen_state'] = [0x13, 0x02, 0x02, [1]]  # state
cmds['VRPM3Race_100012D0'] = [0x80]
cmds['call_10001210'] = [0x9a]
cmds['call_10001400'] = [0x1a, 0x0c, [4], 0x67, 0x6f, 0x21, 0xcc, 0x19, 0x8c, 0x48, 0xe6]  # may be second serial num
cmds['set_race_idle_params'] = [0x21, 0x08, 0xff, 0xff, 0x38, 0x40, 0x00, 0x05, 0x00, 0x01]
cmds['set_datetime'] = [0x22, 0x07, 0x0a, 0x0e, 0x01, 0x0c, 0x01, 0x07, 0xe2]  # may be year, mouth, day
cmds['set_screen_error_mode'] = [0x27, 0x01, 0x00]
cmds['set_cpu_tick_rate'] = [0x25, 0x01, [1]]  # erg address
cmds['get_cpu_tick_rate'] = [0x9d]
cmds['get_erg_info'] = [0x98, 0xc9]
cmds['set_race_starting_physical_address'] = [0x2c, 0x01, 0x01]
cmds['set_race_operation_type'] = [0x1e, 0x01, [1]]  # state
cmds['get_race_lane_request'] = [0x51, 0x02, [1], [1]]  # destination and race line
cmds['set_race_lane_setup'] = [0x0B, 0x02, [1], 0x00]  # race_line
cmds['get_race_lane_check'] = [0x87]  # erg_enumeration_check function
cmds['set_workout_type'] = [0x01, 0x01, 0x01]
cmds['set_race_participant'] = [0x32, [1, 1, ], 0x00]  # len(name) + 2, lane, name
cmds['get_race_participant_count'] = [0x96]
cmds['get_tick_timebase'] = [0x83]
cmds['foo'] = [0x1B]  # unknown function
cmds['get_latched_tick_time'] = [0xC4]
cmds['set_all_race_params'] = [0x1D, 0x04, 0x00, 0x00, 0x00, 0x80, 0x1F, 0x04, 0x00, 0x00, 0x02, 0x00, 0x20, 0x04,
                               0x00, 0x00, 0x0F, 0x00, 0x01, 0x01, 0x03, 0x03, 0x05, 0x80, [4], 0x05, 0x05, 0x80,
                               0x00, 0x00, 0x01, 0xF4, 0x09, 0x01, 0x00]  # distance
cmds['configure_workout'] = [0x14, 0x01, 0x01]
cmds['latch_tick_time'] = [0xD7]
# "02 F0 01 00 76 10 0D 0E 00 00 00 00 42 A8 00 00 44 9B 00 00 46 78 6E F2"
cmds['set_race_start_params'] = [0x0D, ]
# "02 F0 02 00 76 22 33 1D 00 01 00 00 00 00 00 00 00 00 00 00 02 01 00 00 00 00 01 02 00 00 00 00 00 00 00 00 00 C6 BA BC BB F2"
cmds['update_race_data'] = [0x33, ]


# PM3 Specific Short Commands
cmds['CSAFE_PM_GET_WORKOUTTYPE'] = [0x89, [], 0x1A]
cmds['CSAFE_PM_GET_DRAGFACTOR'] = [0xC1, [], 0x1A]
cmds['CSAFE_PM_GET_STROKESTATE'] = [0xBF, [], 0x1A]
cmds['CSAFE_PM_GET_WORKTIME'] = [0xA0, [], 0x1A]
cmds['CSAFE_PM_GET_WORKDISTANCE'] = [0xA3, [], 0x1A]
cmds['CSAFE_PM_GET_ERRORVALUE'] = [0xC9, [], 0x1A]
cmds['CSAFE_PM_GET_WORKOUTSTATE'] = [0x8D, [], 0x1A]
cmds['CSAFE_PM_GET_WORKOUTINTERVALCOUNT'] = [0x9F, [], 0x1A]
cmds['CSAFE_PM_GET_INTERVALTYPE'] = [0x8E, [], 0x1A]
cmds['CSAFE_PM_GET_RESTTIME'] = [0xCF, [], 0x1A]

# PM3 Specific Long Commands
cmds['CSAFE_PM_SET_SPLITDURATION'] = [0x05, [1, 4], 0x1A]  # Time(0)/Distance(128), Duration
cmds['CSAFE_PM_GET_FORCEPLOTDATA'] = [0x6B, [1, ], 0x1A]  # Block Length
cmds['CSAFE_PM_SET_SCREENERRORMODE'] = [0x27, [1, ], 0x1A]  # Disable(0)/Enable(1)
cmds['CSAFE_PM_GET_HEARTBEATDATA'] = [0x6C, [1, ], 0x1A]  # Block Length

# resp[0xCmd_Id] = [COMMAND_NAME, [Bytes, ...]]
# negative number for ASCII
# use absolute max number for variable, (getid & getcaps)
resp = {}

# Response Data to Short Commands
resp[0x80] = ['CSAFE_GETSTATUS_CMD', [0, ]]  # Status
resp[0x81] = ['CSAFE_RESET_CMD', [0, ]]
resp[0x82] = ['CSAFE_GOIDLE_CMD', [0, ]]
resp[0x83] = ['CSAFE_GOHAVEID_CMD', [0, ]]
resp[0x85] = ['CSAFE_GOINUSE_CMD', [0, ]]
resp[0x86] = ['CSAFE_GOFINISHED_CMD', [0, ]]
resp[0x87] = ['CSAFE_GOREADY_CMD', [0, ]]
resp[0x88] = ['CSAFE_BADID_CMD', [0, ]]
resp[0x91] = ['CSAFE_GETVERSION_CMD', [1, 1, 1, 2, 2]]  # Mfg ID, CID, Model, HW Version, SW Version
resp[0x92] = ['CSAFE_GETID_CMD', [-5, ]]  # ASCII Digit (variable)
resp[0x93] = ['CSAFE_GETUNITS_CMD', [1, ]]  # Units Type
resp[0x94] = ['CSAFE_GETSERIAL_CMD', [-9, ]]  # ASCII Serial Number
resp[0x9B] = ['CSAFE_GETODOMETER_CMD', [4, 1]]  # Distance, Units Specifier
resp[0x9C] = ['CSAFE_GETERRORCODE_CMD', [3, ]]  # Error Code
resp[0xA0] = ['CSAFE_GETTWORK_CMD', [1, 1, 1]]  # Hours, Minutes, Seconds
resp[0xA1] = ['CSAFE_GETHORIZONTAL_CMD', [2, 1]]  # Distance, Units Specifier
resp[0xA3] = ['CSAFE_GETCALORIES_CMD', [2, ]]  # Total Calories
resp[0xA4] = ['CSAFE_GETPROGRAM_CMD', [1, ]]  # Program Number
resp[0xA6] = ['CSAFE_GETPACE_CMD', [2, 1]]  # Stroke Pace, Units Specifier
resp[0xA7] = ['CSAFE_GETCADENCE_CMD', [2, 1]]  # Stroke Rate, Units Specifier
resp[0xAB] = ['CSAFE_GETUSERINFO_CMD', [2, 1, 1, 1]]  # Weight, Units Specifier, Age, Gender
resp[0xB0] = ['CSAFE_GETHRCUR_CMD', [1, ]]  # Beats/Min
resp[0xB4] = ['CSAFE_GETPOWER_CMD', [2, 1]]  # Stroke Watts

# Response Data to Long Commands
resp[0x01] = ['CSAFE_AUTOUPLOAD_CMD', [0, ]]
resp[0x10] = ['CSAFE_IDDIGITS_CMD', [0, ]]
resp[0x11] = ['CSAFE_SETTIME_CMD', [0, ]]
resp[0x12] = ['CSAFE_SETDATE_CMD', [0, ]]
resp[0x13] = ['CSAFE_SETTIMEOUT_CMD', [0, ]]
resp[0x1A] = ['CSAFE_SETUSERCFG1_CMD', [0, ]]  # PM3 Specific Command ID
resp[0x20] = ['CSAFE_SETTWORK_CMD', [0, ]]
resp[0x21] = ['CSAFE_SETHORIZONTAL_CMD', [0, ]]
resp[0x23] = ['CSAFE_SETCALORIES_CMD', [0, ]]
resp[0x24] = ['CSAFE_SETPROGRAM_CMD', [0, ]]
resp[0x34] = ['CSAFE_SETPOWER_CMD', [0, ]]
resp[0x70] = ['CSAFE_GETCAPS_CMD', [11, ]]  # Depended on Capability Code (variable)

# Response Data to Extended Long Commands
resp[0x76] = ['CSAFE_SETPMCFG_CMD', [0, ]]
resp[0x77] = ['CSAFE_GETPMCFG_CMD', [1, ]]
resp[0x7e] = ['CSAFE_GETPMCFG_CMD', [0, ]]

# Response Data to PM3 Specific Short Commands
resp[0x1A89] = ['CSAFE_PM_GET_WORKOUTTYPE', [1, ]]  # Workout Type
resp[0x1AC1] = ['CSAFE_PM_GET_DRAGFACTOR', [1, ]]  # Drag Factor
resp[0x1ABF] = ['CSAFE_PM_GET_STROKESTATE', [1, ]]  # Stroke State
# Work Time (seconds * 100), Fractional Work Time (1/100)
resp[0x1AA0] = ['CSAFE_PM_GET_WORKTIME', [4, 1]]
# Work Distance (meters * 10), Fractional Work Distance (1/10)
resp[0x1AA3] = ['CSAFE_PM_GET_WORKDISTANCE', [4, 1]]
resp[0x1AC9] = ['CSAFE_PM_GET_ERRORVALUE', [2, ]]  # Error Value
resp[0x1A8D] = ['CSAFE_PM_GET_WORKOUTSTATE', [1, ]]  # Workout State
resp[0x1A9F] = ['CSAFE_PM_GET_WORKOUTINTERVALCOUNT', [1, ]]  # Workout Interval Count
resp[0x1A8E] = ['CSAFE_PM_GET_INTERVALTYPE', [1, ]]  # Interval Type
resp[0x1ACF] = ['CSAFE_PM_GET_RESTTIME', [2, ]]  # Rest Time

# Response Data to PM3 Specific Long Commands
resp[0x1A05] = ['CSAFE_PM_SET_SPLITDURATION', [0, ]]  # No variables returned !! double check
resp[0x1A6B] = ['CSAFE_PM_GET_FORCEPLOTDATA', [
    1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]  # Bytes read, data ...
resp[0x1A27] = ['CSAFE_PM_SET_SCREENERRORMODE', [0, ]]  # No variables returned !! double check
resp[0x1A6C] = ['CSAFE_PM_GET_HEARTBEATDATA', [
    1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]  # Bytes read, data ...

race_cmds = {}

race_cmds[0xE1] = 'reset_erg_num'
race_cmds[0x82] = 'get_serial_num'
race_cmds[0x10] = 'set_erg_num'
race_cmds[0x50] = 'get_erg_num_confirm'
race_cmds[0x13] = 'set_screen_state'
race_cmds[0x80] = 'VRPM3Race_100012D0'
race_cmds[0x9A] = 'call_10001210'
race_cmds[0x1A] = 'call_10001400'
race_cmds[0x21] = 'set_race_idle_params'
race_cmds[0x22] = 'set_datetime'
race_cmds[0x27] = 'set_screen_error_mode'
race_cmds[0x25] = 'set_cpu_tick_rate'
race_cmds[0x9D] = 'get_cpu_tick_rate'
race_cmds[0x98] = 'get_erg_info'
race_cmds[0x2C] = 'set_race_starting_physical_address'
race_cmds[0x1E] = 'set_race_operation_type'
race_cmds[0x98] = 'get_erg_info'
race_cmds[0x51] = 'get_race_lane_request'
race_cmds[0x0B] = 'set_race_lane_setup'
race_cmds[0x87] = 'get_race_lane_check'
race_cmds[0x01] = 'set_workout_type'
race_cmds[0x32] = 'set_race_participant'
race_cmds[0x96] = 'get_race_participant_count'
race_cmds[0x83] = 'get_tick_timebase'
race_cmds[0x1B] = 'foo'
race_cmds[0xC4] = 'get_latched_tick_time'
race_cmds[0x1D] = 'set_all_race_params'
race_cmds[0x14] = 'configure_workout'
race_cmds[0xD7] = 'latch_tick_time'
race_cmds[0x0D] = 'set_race_start_params'
race_cmds[0x33] = 'update_race_data'
# TODO unknown commands
race_cmds[0x8D] = 'workout_state'  # temp from this dict
race_cmds[0x99] = 'bar'  # ????
race_cmds[0x6A] = 'bar_bar'  # ????
race_cmds[0x35] = 'barbar_bar'  # time 0x77
