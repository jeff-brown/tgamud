""" weapon class """
import yaml


class Key():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/keys.yaml", "rb") as stream:
            try:
                self.keys = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
