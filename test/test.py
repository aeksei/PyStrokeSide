import sys
from PyStrokeSide import PyStrokeSide

TIMEOUT = 0


def byte_staffing(cmd):
    while "f3 00" in cmd:
        cmd = cmd.replace("f3 00", "f0")
    while "f3 01" in cmd:
        cmd = cmd.replace("f3 01", "f1")
    while "f3 02" in cmd:
        cmd = cmd.replace("f3 02", "f2")
    while "f3 03" in cmd:
        cmd = cmd.replace("f3 03", "f3")

    return cmd


def test_team_race(test_race):
    file_with_hex_cmd = "team.race"
    test_race.timeout = TIMEOUT

    with open(file_with_hex_cmd, "r") as f:
        for line in f:
            cmd = line[:-1]
            cmd = byte_staffing(cmd)
            cmd = [int(i, 16) for i in cmd.split(" ")]
            test_race.handler(cmd)


def test_single_race(test_race):
    file_with_hex_cmd = "single.race"
    test_race.timeout = TIMEOUT

    with open(file_with_hex_cmd, "r") as f:
        for line in f:
            cmd = line[:-1]
            cmd = byte_staffing(cmd)
            cmd = [int(i, 16) for i in cmd.split(" ")]
            test_race.handler(cmd)


if __name__ == "__main__":
    race = PyStrokeSide()

    try:
        test_single_race(race)
        test_team_race(race)
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        race.logger.critical("{} {}".format(e, e.args))
    finally:
        race.logger.info("Close sniffer")
        sys.exit()
