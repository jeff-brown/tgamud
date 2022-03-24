""" weapon class """
import yaml


class Door():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/doors.yaml", "rb") as stream:
            try:
                self.doors = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
