""" species class """
import yaml


class MonsterStats():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/monsterstats.yaml", "rb") as stream:
            try:
                self.monsterstats = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
