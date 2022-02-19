""" weapon class """
import yaml


class Weapon():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/weapons.yaml", "rb") as stream:
            try:
                self.weapons = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
