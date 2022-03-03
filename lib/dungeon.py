""" dungeon class """
import yaml


class Dungeon():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        self.grid = []

        with open("conf/dungeons.yaml", "rb") as stream:
            try:
                _dungeons = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.dungeons = _dungeons

        self._town = [
            [0,  0,  0,  0,  0],
            [0,  0,  1,  0,  0],
            [0,  10, 2,  11, 0],
            [0,  0,  12, 0,  0],
            [0,  9,  3,  8,  0],
            [0,  0,  12, 0,  0],
            [0,  6,  4,  7,  0],
            [0,  0,  5,  0,  0],
            [0,  0,  0,  0,  0]
        ]

        self.grid.append(self._town)
