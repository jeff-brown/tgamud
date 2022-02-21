""" Classes class """
import yaml


class Classes():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/classes.yaml", "rb") as stream:
            try:
                self.classes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
