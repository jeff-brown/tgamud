""" dungeon class """
import json
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

        with open("dungeons/t1.json", "rb") as stream:
            try:
                _t1 = json.loads(stream.read())
            except Exception as exc:
                print(exc)

        with open("dungeons/d0.json", "rb") as stream:
            try:
                _d0 = json.loads(stream.read())
            except Exception as exc:
                print(exc)

        with open("dungeons/d1.json", "rb") as stream:
            try:
                _d1 = json.loads(stream.read())
            except Exception as exc:
                print(exc)

        with open("dungeons/d9.json", "rb") as stream:
            try:
                _d9 = json.loads(stream.read())
            except Exception as exc:
                print(exc)

        self.dungeons = _dungeons

        self.grid.append(_d0)
        self.grid.append(_t1)
        self.grid.append(_d1)
        self.grid.append(_d9)
