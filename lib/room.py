""" rooms class """
import yaml

from lib.armor import Armor
from lib.weapon import Weapon
from lib.gear import Gear
from lib.magic import Magic


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

        _magic = Magic()

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
                "etype": "temple",
                "value": 10,
                "condition": "hurt",
                "equip": False,
                "inv": False
            },
            {
                "type": "curing",
                "etype": "temple",
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
                "etype": "tavern",
                "value": 10,
                "condition": "thirst",
                "equip": False,
                "inv": False
            },
            {
                "type": "food",
                "etype": "tavern",
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
                "etype": "magic",
                "value": 10000,
                "condition": "light",
                "equip": False,
                "weight": 1,
                "inv": True
            },
            {
                "type": "hearthstone",
                "etype": "magic",
                "value": 100000,
                "condition": "return",
                "equip": False,
                "weight": 1,
                "inv": True
            },
            {

                "type": "soulstone",
                "etype": "magic",
                "value": 1000000,
                "condition": "death",
                "equip": False,
                "weight": 1,
                "inv": True
            },

        ]

        # guildhall
        self.rooms[2]["items"] = [
            {
                "type": "training",
                "etype": "guild",
                "value": 100,
                "condition": "level",
                "equip": False,
                "inv": False
            }
        ]

        self.rooms[2]["spells"] = _magic.magics
