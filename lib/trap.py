""" weapon class """
import yaml


class Trap():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/traps.yaml", "rb") as stream:
            try:
                self.traps = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
