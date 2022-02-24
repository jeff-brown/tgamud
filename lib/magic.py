""" magic class """
import yaml


class Magic():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/magics.yaml", "rb") as stream:
            try:
                self.magics = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
