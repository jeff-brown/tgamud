""" weapon class """
import time
import yaml

from lib.condition import Condition
from lib.classes import Classes
from lib.dice import Dice


class Trap():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/traps.yaml", "rb") as stream:
            try:
                self.traps = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self._condition = Condition()
        self._classes = Classes()
        self._dice = Dice()

    def detect_trap(self, player, num):
        """ try to detect trap """
        trap = self.traps[num]

        if time.time() - trap["detected"] < 60:
            return True, trap["detect"]

        if self._classes.get_modifier(player["wisdom"]) \
                + self._dice.roll([1, 20]) \
                > trap["dc"]:

            trap["detected"] = time.time()
            return True, trap["detect"]

        return False, trap["not_detect"]

    def avoid_trap(self, player, num):
        """ step on a trap, suffer consequences """
        message = None
        trap = self.traps[num]

        if self._classes.get_modifier(player["dexterity"]) \
                + self._dice.roll([1, 20]) \
                > trap["dc"]:

            message = trap["avoid"]
            trap["detected"] = time.time()

        else:
            damage = self._dice.roll(trap["damage"])
            player["current_hp"] -= damage
            message = trap["not_avoid"].format(damage)

        return message

    def disable_trap(self, player, num):
        """ rogues can disable traps with theives tools """
