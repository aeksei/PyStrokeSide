#!/usr/bin/env python
#Copyright (c) 2011 Sam Gambrell, 2016-2017 Michael Droogleever
#Licensed under the Simplified BSD License.

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

from warnings import warn
from pyrow.csafe import csafe_dic
import numpy as np
import struct as st
import datetime
from random import randint


def cmd2hex(list_int):
    return ' '.join(['{:02X}'.format(i) for i in list_int])


def gen_auth_code(serial):
    v8 = np.uint32(serial)
    v6 = np.uint32(serial)
    v5 = np.uint32(0)
    a3 = [np.uint32(0x01071984),
          np.uint32(0x12221959),
          np.uint32(0x12301958),
          np.uint32(0x03191960)]

    for i in range(32):
        v8 = np.uint32(v8 + a3[v5 & 3] + (v5 ^ v6) + ((v6 >> 5) ^ np.uint32(16 * v6)))
        v5 = np.uint32(v5 - 1640531527)
        v6 = np.uint32(v6 + a3[(v5 >> 11) & 3] + (v5 ^ v8) + ((v8 >> 5) ^ np.uint32(16 * v8)))

    return __int2bytes(4, serial)[::-1] + __int2bytes(4, v8)[::-1] + __int2bytes(4, v6)[::-1]


def get_start_param(latch_time):
    local_2 = 309  # 490 from ida pro
    v8 = int(randint(0, 32767) * (3000 - 1500) / 32767)
    v9 = 1500 + local_2 + v8
    v19 = randint(0, 32767)
    v8 = int(v19 * (2000 - 1500) / 32767)
    v10 = 1500 + v9 + v8

    v15 = 256
    p1 = int(local_2 / 1000 * v15)
    p2 = int(v9 / 1000 * v15)
    p3 = int(v10 / 1000 * v15)

    hx = cmd2hex(latch_time).replace(' ', '')
    latch_time = int(st.unpack(">f", st.pack(">i", int(hx, 16)))[0])

    p1 += latch_time
    p2 += latch_time
    p3 += latch_time

    return __int2bytes(4, p1)[::-1] + __int2bytes(4, p2)[::-1] + __int2bytes(4, p3)[::-1]


def __int2bytes(numbytes, integer):
    if not 0 <= integer <= 2 ** (8 * numbytes):
        raise ValueError("Integer is outside the allowable range")

    byte = []
    for k in range(numbytes):
        calcbyte = (integer >> (8 * k)) & 0xFF
        byte.append(calcbyte)

    return byte


def __bytes2int(raw_bytes):
    num_bytes = len(raw_bytes)
    raw_bytes = raw_bytes[::-1]
    integer = 0

    for k in range(num_bytes):
        integer = (raw_bytes[k] << (8 * k)) | integer

    return integer


def __bytes2ascii(raw_bytes):
    word = ""
    for letter in raw_bytes:
        word += chr(letter)

    return word


def get_time_cmd():
    now = datetime.datetime.now()  # Get current date and time
    cmd = [now.hour % 12, now.minute, 0x01, now.month, now.day]
    cmd.extend(__int2bytes(2, now.year)[::-1])
    return cmd

#for sending
def write(arguments):

    #priming variables
    i = 0
    message = []
    wrapper = 0
    wrapped = []
    maxresponse = 3 #start & stop flag & status

    #loop through all arguments
    while i < len(arguments):
        extended_frame = False
        arg = arguments[i]
        if isinstance(arg, list):
            # for Extended Frame Format
            extended_frame = True
            dst = arg[0]
            src = arg[1]
            cmdprop = [arg[2], []]
            cmdprop[1] = [1] * arg[3]
        else:
            cmdprop = csafe_dic.cmds[arg]
        command = []

        #load variables if command is a Long Command
        if len(cmdprop[1]) != 0:
            for varbytes in cmdprop[1]:
                i += 1
                intvalue = arguments[i]
                value = __int2bytes(varbytes, intvalue)
                command.extend(value)

            #data byte count
            cmdbytes = len(command)
            command.insert(0, cmdbytes)

        #add command id
        command.insert(0, cmdprop[0])

        #closes wrapper if required
        if len(wrapped) > 0 and (len(cmdprop) < 3 or cmdprop[2] != wrapper):
            wrapped.insert(0, len(wrapped)) #data byte count for wrapper
            wrapped.insert(0, wrapper) #wrapper command id
            message.extend(wrapped) #adds wrapper to message
            wrapped = []
            wrapper = 0

        #create or extend wrapper
        if len(cmdprop) == 3: #checks if command needs a wrapper
            if wrapper == cmdprop[2]: #checks if currently in the same wrapper
                wrapped.extend(command)
            else: #creating a new wrapper
                wrapped = command
                wrapper = cmdprop[2]
                maxresponse += 2

            command = [] #clear command to prevent it from getting into message

        #max message length
        cmdid = cmdprop[0] | (wrapper << 8)
        #double return to account for stuffing
        maxresponse += abs(sum(csafe_dic.resp[cmdid][1])) * 2 + 1

        #add completed command to final message
        message.extend(command)

        i += 1

    #closes wrapper if message ended on it
    if len(wrapped) > 0:
        wrapped.insert(0, len(wrapped)) #data byte count for wrapper
        wrapped.insert(0, wrapper) #wrapper command id
        message.extend(wrapped) #adds wrapper to message

    #prime variables
    checksum = 0x0
    j = 0

    #checksum and byte stuffing
    while j < len(message):
        #calculate checksum
        checksum = checksum ^ message[j]

        #byte stuffing
        if 0xF0 <= message[j] <= 0xF3:
            message.insert(j, csafe_dic.Byte_Stuffing_Flag)
            j += 1
            message[j] = message[j] & 0x3

        j += 1

    #add checksum to end of message
    message.append(checksum)

    #start & stop frames
    if extended_frame:
        message.insert(0, src)
        message.insert(0, dst)
        message.insert(0, csafe_dic.Extended_Frame_Start_Flag)
    else:
        message.insert(0, csafe_dic.Standard_Frame_Start_Flag)
    message.append(csafe_dic.Stop_Frame_Flag)

    #check for frame size (96 bytes)
    if len(message) > 96:
        warn("Message is too long: " + len(message))

    #report IDs
    if extended_frame:
        maxmessage = 121
    else:
        maxmessage = max(len(message) + 1, maxresponse)
    #
    if maxmessage <= 21:
        message.insert(0, 0x01)
        message += [0] * (21 - len(message))
    elif maxmessage <= 63:
        message.insert(0, 0x04)
        message += [0] * (63 - len(message))
    elif (len(message) + 1) <= 121:
        message.insert(0, 0x02)
        message += [0] * (121 - len(message))
        if maxresponse > 121:
            warn("Response may be too long to recieve.  Max possible length " + str(maxresponse))
    else:
        warn("Message too long.  Message length " + str(len(message)))
        message = []

    return message


def __check_message(message):
    #prime variables
    i = 0
    checksum = 0

    #checksum and unstuff
    while i < len(message):
        #byte unstuffing
        if message[i] == csafe_dic.Byte_Stuffing_Flag:
            stuffvalue = message.pop(i + 1)
            message[i] = 0xF0 | stuffvalue

        #calculate checksum
        checksum = checksum ^ message[i]

        i = i + 1

    #checks checksum
    if checksum != 0:
        warn("Checksum error")
        return []

    #remove checksum from  end of message
    del message[-1]

    return message

#for recieving!!
def read(transmission):
    #prime variables
    message = []
    stopfound = False

    #reportid = transmission[0]
    startflag = transmission[1]

    if startflag == csafe_dic.Extended_Frame_Start_Flag:
        destination = transmission[2]
        source = transmission[3]
        j = 4
    elif startflag == csafe_dic.Standard_Frame_Start_Flag:
        j = 2
    else:
        warn("No Start Flag found.")
        return []

    while j < len(transmission):
        if transmission[j] == csafe_dic.Stop_Frame_Flag:
            stopfound = True
            break
        message.append(transmission[j])
        j += 1

    if not stopfound:
        warn("No Stop Flag found.")
        return []

    message = __check_message(message)
    status = message.pop(0)

    #prime variables
    response = {'CSAFE_GETSTATUS_CMD' : [status,]}
    k = 0
    wrapend = -1
    wrapper = 0x0

    #loop through complete frames
    while k < len(message):
        result = []

        #get command name
        msgcmd = message[k]
        if k <= wrapend:
            msgcmd = wrapper | msgcmd #check if still in wrapper
        msgprop = csafe_dic.resp[msgcmd]
        k = k + 1

        #get data byte count
        bytecount = message[k]
        k = k + 1

        #if wrapper command then gets command in wrapper
        if msgprop[0] == 'CSAFE_SETUSERCFG1_CMD':
            wrapper = message[k - 2] << 8
            wrapend = k + bytecount - 1
            if bytecount: #If wrapper length != 0
                msgcmd = wrapper | message[k]
                msgprop = csafe_dic.resp[msgcmd]
                k = k + 1
                bytecount = message[k]
                k = k + 1

        #special case for capability code, response lengths differ based off capability code
        if msgprop[0] == 'CSAFE_GETCAPS_CMD':
            msgprop[1] = [1,] * bytecount

        #special case for get id, response length is variable
        if msgprop[0] == 'CSAFE_GETID_CMD':
            msgprop[1] = [(-bytecount),]

        #checking that the recieved data byte is the expected length, sanity check
        if abs(sum(msgprop[1])) != 0 and bytecount != abs(sum(msgprop[1])):
            warn("Warning: bytecount is an unexpected length")

        if msgprop[0] == 'CSAFE_SETPMCFG_CMD':
            msgprop[1] = [1, ] * bytecount

        if msgprop[0] == 'CSAFE_GETPMCFG_CMD':
            msgprop[1] = [1, ] * bytecount

        #extract values
        for numbytes in msgprop[1]:
            raw_bytes = message[k:k + abs(numbytes)]
            value = (__bytes2int(raw_bytes) if numbytes >= 0 else __bytes2ascii(raw_bytes))
            result.append(value)
            k = k + abs(numbytes)

        response[msgprop[0]] = result

    return response


if __name__ == '__main__':
    print(__bytes2int([0x19, 0xa6, 0x84, 0x95]))
    print(__bytes2int([0x19, 0xa6, 0x84, 0xda]))
