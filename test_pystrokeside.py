from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace

if __name__ == "__main__":
    erg_num = {}

    ergs = list(pyrow.find())

    erg = ergs[0]
    master_erg = PyErgRace(erg)

    # Number ALL ergs
    master_erg.reset_erg_num()

    while True:
        serial = master_erg.get_serial_num()
        if serial:
            erg_num[serial] = 0x01
            master_erg.set_erg_num(serial, erg_num[serial])
            master_erg.get_erg_num_confirm(erg_num[serial], serial)
            break

    master_erg.set_race_starting_physical_address(destination=0x01)
    master_erg.set_race_operation_type(destination=0x01, state=0x04)

    master_erg.set_race_starting_physical_address(destination=0xFF)
    master_erg.set_race_operation_type(destination=0xFF, state=0x04)

    master_erg.set_screen_state(destination=0xFF, state=0x01)



