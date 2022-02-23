""" armor class """
import yaml


class Armor():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        self.armors = []

        with open("conf/armors.yaml", "rb") as stream:
            try:
                __armors = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.armors = __armors
