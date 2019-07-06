from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace
import time
import usb.core
import usb.util

if __name__ == "__main__":
    ergs = list(pyrow.find())

    erg = ergs[0]
    master_erg = PyErgRace(erg)

    master_erg.reset_erg_num()

    serial = []
    while not serial:
        serial = master_erg.get_serial_num()
    print(serial)

