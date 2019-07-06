import os
import logging
from logging.handlers import RotatingFileHandler


def logger(name):
    if "LogData" not in os.listdir():
        os.mkdir("LogData")
    if "Log" not in os.listdir(os.getcwd() + "\\LogData"):
        os.mkdir(os.getcwd() + "\\LogData" + "\\Log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    path = os.getcwd() + "\\LogData" + "\\Log"
    filehandler = RotatingFileHandler(path + "\\PyStrokeSide.log",
                                      maxBytes=25 * 1024 * 1024,
                                      backupCount=50)

    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(filehandler)

    return logger


def race_logger(filename):
    race_logger = logging.getLogger("race")
    race_logger.setLevel(logging.INFO)

    if "RaceLog" not in os.listdir(os.getcwd() + "\\LogData"):
        os.mkdir(os.getcwd() + "\\LogData" + "\\RaceLog")

    path = os.getcwd() + "\\LogData" + "\\RaceLog" + "\\"

    racehandler = logging.FileHandler(path + filename)
    racehandler.setLevel(logging.DEBUG)
    race_logger.addHandler(racehandler)

    return race_logger


def raw_logger():
    if "RawCommands" not in os.listdir(os.getcwd() + "\\LogData"):
        os.mkdir(os.getcwd() + "\\LogData" + "\\RawCommands")

    raw_logger = logging.getLogger("raw")
    raw_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    path = os.getcwd() + "\\LogData" + "\\RawCommands" + "\\"
    filename = "RawCommands.log"
    filehandler = RotatingFileHandler(path + filename,
                                      maxBytes=25 * 1024 * 1024,
                                      backupCount=50)

    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(formatter)

    raw_logger.addHandler(filehandler)

    return raw_logger
