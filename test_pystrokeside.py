from pyrow import pyrow
from pyrow.pyrow_race import PyErgRace

if __name__ == "__main__":
    ergs = list(pyrow.find())
    erg = ergs[0]
    erg.set_configuration()
    master_erg = PyErgRace(erg)
    master_erg.reset_erg_num()
