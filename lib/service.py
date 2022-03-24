""" weapon class """
import yaml


class Service():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/services.yaml", "rb") as stream:
            try:
                self.services = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
