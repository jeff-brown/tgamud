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
<<<<<<< HEAD
                "value": 10,
=======
                "value": 100,
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c
                "condition": "hurt",
                "equip": False,
                "inv": False
            },
            {
                "type": "curing",
<<<<<<< HEAD
                "value": 10,
=======
                "value": 100,
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c
                "condition": "poison",
                "equip": False,
                "inv": False
            }
        ]

        # tavern
        self.rooms[11]["items"] = [
            {
                "type": "drink",
<<<<<<< HEAD
                "value": 10,
=======
                "value": 100,
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c
                "condition": "thirst",
                "equip": False,
                "inv": False
            },
            {
                "type": "food",
<<<<<<< HEAD
                "value": 10,
=======
                "value": 100,
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c
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
<<<<<<< HEAD
                "type": "hearthstone",
                "value": 100000,
                "condition": "return",
                "equip": False,
                "inv": True
            },
            {
=======
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c
                "type": "soulstone",
                "value": 1000000,
                "condition": "death",
                "equip": False,
                "inv": True
            },
<<<<<<< HEAD

=======
            {
                "type": "hearthstone",
                "value": 100000,
                "condition": "return",
                "equip": False,
                "inv": True
            }
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c
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
