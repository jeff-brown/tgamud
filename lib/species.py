""" species class """
import yaml


class Species():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/species.yaml", "rb") as stream:
            try:
                self.species = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
