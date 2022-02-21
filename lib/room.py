""" rooms class """
import yaml

from lib.armor import Armor
from lib.weapon import Weapon
from lib.gear import Gear


class Room():
    """
    This class contains all of the functions to allow the game to operate

            self._grid = [
                [0,  0,  0,  0,  0],
                [0,  0,  1,  0,  0],
                [0,  10, 2,  11, 0],
                [0,  0,  12, 0,  0],
                [0,  9,  3,  8,  0],
                [0,  0,  12, 0,  0],
                [0,  6,  4,  7,  0],
                [0,  0,  5,  0,  0],
                [0,  0,  0,  0,  0]
            ]
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

        _gear = Gear()

        # armor shop
        self.rooms[6]["items"] = _armor.armors

        # weapon shop
        self.rooms[7]["items"] = _weapon.weapons

        # adventure gear shop
        self.rooms[10]["items"] = _gear.gears

        # temple
        #   equip: true
        #   inv: true
        self.rooms[9]["items"] = [
            {
                "type": "healing",
                "value": 10,
                "condition": "hurt",
                "equip": False,
                "inv": False
            },
            {
                "type": "curing",
                "value": 10,
                "condition": "poison",
                "equip": False,
                "inv": False
            }
        ]

        # tavern
        self.rooms[11]["items"] = [
            {
                "type": "drink",
                "value": 10,
                "condition": "thirst",
                "equip": False,
                "inv": False
            },
            {
                "type": "food",
                "value": 10,
                "condition": "hunger",
                "equip": False,
                "inv": False
            }
        ]

        # magic shop
        self.rooms[5]["items"] = [
            {
                "type": "glowstone",
                "value": 10000,
                "condition": "light",
                "equip": False,
                "inv": True
            },
            {
                "type": "hearthstone",
                "value": 100000,
                "condition": "return",
                "equip": False,
                "inv": True
            },
            {

                "type": "soulstone",
                "value": 1000000,
                "condition": "death",
                "equip": False,
                "inv": True
            },

        ]

        # guildhall
        self.rooms[2]["items"] = [
            {
                "type": "leveling",
                "value": 100,
                "condition": "level",
                "equip": False,
                "inv": False
            }
        ]
