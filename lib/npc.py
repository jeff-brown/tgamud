""" npc class """
import yaml


class Npc():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/npcs.yaml", "rb") as stream:
            try:
                self.npcs = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
