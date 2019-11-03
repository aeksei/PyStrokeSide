import json
import numpy as np
import logging.config
from pyrow.csafe.csafe_cmd import __int2bytes, __bytes2int

_int2bytes = __int2bytes
_bytes2int = __bytes2int


class PyErgRaceData:
    def __init__(self):
        with open("logging.json", "r") as f:
            logging.config.dictConfig(json.load(f))
        self.PySSRace_logger = logging.getLogger("PySSRace")
        self.race_data = dict()
        self.count_boats = None
        self.team_size = None
        self.duration = None
        self.leader_board = None
        self.finished_participant = dict()

    def set_config_race(self, count_boats, team_size, duration):
        self.PySSRace_logger.info("Set configuration in pyrow_data")
        self.count_boats = count_boats
        self.team_size = team_size
        self.duration = duration

        self.finished_participant = {line_number: False for line_number in range(self.count_boats)}

        for line_number in range(1, self.count_boats + 1):
            self.race_data[line_number] = dict(lane_number=line_number,
                                               distance=0,
                                               time=0,
                                               stroke=0,
                                               split=0)

    def get_race_data(self):
        race_data = dict()
        for position, data in self.race_data.items():
            if data['time'] > 5 and data['distance']:
                race_data[position] = data
            if (data['time'] > 20 and data['distance'] == 0) or (data['distance'] >= self.duration):
                if not self.finished_participant[data['lane_number']]:
                    self.PySSRace_logger.info("Participant with {} line_number finished"
                                              " with {} distance and {} time".format(data['lane_number'],
                                                                                     data['distance'],
                                                                                     data['time']))
                self.finished_participant[data['lane_number']] = True
            else:
                self.finished_participant[data['lane_number']] = False
        return sorted(race_data.values(), key=lambda data: data['distance'], reverse=True)

    def get_leader_board(self, boat):
        is_leader = False
        leader_board = []
        for position, leader in enumerate(self.get_race_data()[:4]):
            if leader['lane_number'] == boat['lane_number']:
                is_leader = True
            leader_board.append(leader['lane_number'])
            leader_board.append(position + 1)
            delta = (boat['distance'] - leader['distance']) * 10
            leader_board.extend(_int2bytes(4, np.uint32(delta))[::-1])

        if is_leader:  # ToDo if boat not in leader board then set fourth position
            pass

        length = len(leader_board)
        if length != 24:
            leader_board.extend([0] * (24 - length))

        return leader_board

    def get_update_race_data(self, line_number):
        boat = self.race_data[line_number]
        return self.get_leader_board(boat)

    def set_update_race_data(self, line_number, resp):
        distance = round(_bytes2int(resp[7:11]) * 0.1, 1)  # dist * 10
        time = round(_bytes2int(resp[13:17]) * 0.01, 2)  # time * 100
        stroke = resp[17]  # stroke
        split = round(500 * (time / distance) if distance != 0 else 0, 2)

        self.race_data[line_number] = dict(lane_number=line_number,
                                           distance=distance,
                                           time=time,
                                           stroke=stroke,
                                           split=split)
        self.PySSRace_logger.debug("Participant have result {}".format(self.race_data[line_number]))

    def is_finished_race(self):
        if sum(self.finished_participant.values()) == self.count_boats:
            self.PySSRace_logger.info("All participant finished race")
            return True
        else:
            return False
