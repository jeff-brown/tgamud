""" rooms class """
import yaml

from lib.armor import Armor
from lib.weapon import Weapon


class Room():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/rooms.yaml", "rb") as stream:
            try:
                self.rooms = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        _armor = Armor()

        _weapon = Weapon()

        self.rooms[6]["items"] = _armor.armors

        self.rooms[7]["items"] = _weapon.weapons
