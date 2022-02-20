""" monsters class """
import yaml


class Monster():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/monsters.yaml", "rb") as stream:
            try:
                self.mm = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)