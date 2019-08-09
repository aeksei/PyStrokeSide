import numpy as np
from pyrow.csafe.csafe_cmd import __int2bytes, __bytes2int

_int2bytes = __int2bytes
_bytes2int = __bytes2int


class PyErgRaceData:
    def __init__(self):
        self.race_data = None
        self.count_boats = None
        self.team_size = None
        self.duration = None
        self.leader_board = None

    def set_config_race(self, count_boats, team_size, duration):
        self.race_data = {}
        self.count_boats = count_boats
        self.team_size = team_size
        self.duration = duration

        for line_number in range(1, self.count_boats + 1):
            self.race_data[line_number] = dict(lane_number=line_number,
                                               distance=0,
                                               time=0,
                                               stroke=0,
                                               split=0)

    def get_race_data(self):
        return sorted(self.race_data.values(), key=lambda data: data['distance'], reverse=True)

    def get_update_race_data(self, line_number):
        boat = self.race_data[line_number]
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
            leader_board.extend([0]*(24 - length))

        return leader_board









