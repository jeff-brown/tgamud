""" rooms class """
import yaml

from lib.armor import Armor
from lib.weapon import Weapon
from lib.gear import Gear
from lib.magic import Magic
from lib.service import Service
from lib.trap import Trap
from lib.key import Key
from lib.door import Door


class Room():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/t1.yaml", "rb") as stream:
            try:
                self._t1 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("conf/d1.yaml", "rb") as stream:
            try:
                self._d1 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("conf/d2.yaml", "rb") as stream:
            try:
                self._d2 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("conf/d3.yaml", "rb") as stream:
            try:
                self._d3 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.rooms = []

        self._trap = Trap()

        self._door = Door()

        self._key = Key()

        _armor = Armor()

        _weapon = Weapon()

        _gear = Gear()

        _magic = Magic()

        _service = Service()

        # armor shop
        self._t1[6]["items"] = _armor.armors

        # weapon shop
        self._t1[7]["items"] = _weapon.weapons

        # adventure gear shop
        self._t1[10]["items"] = [
            x for x in _gear.gears if x['etype'] == 'gear']

        # temple
        self._t1[9]["items"] = [
            x for x in _service.services if x['etype'] == ' temple']

        # tavern
        self._t1[11]["items"] = [
            x for x in _service.services if x['etype'] == 'tavern']

        # magic shop
        self._t1[5]["items"] = [
            x for x in _gear.gears if x['etype'] == 'magic']

        # guildhall
        self._t1[2]["items"] = [
            x for x in _service.services if x['etype'] == 'guild']

        self._t1[2]["spells"] = _magic.magics

        self._d0 = []
        self._d9 = []
        self._d0.append(self._t1[0])
        self._d9.append(self._t1[0])

        self.rooms.append(self._d0)
        self.rooms.append(self._t1)
        self.rooms.append(self._d1)
        self.rooms.append(self._d2)
        self.rooms.append(self._d3)
        self.rooms.append(self._d9)

    def process_trap(self, player):
        """ what happens when you walk into a trap dummy """

    def process_door(self, player):
        """ can you open this door do you have the key """
