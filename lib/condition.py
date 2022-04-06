""" condition class """
import time
import yaml

from lib.dice import Dice


class Condition():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        self.conditions = []

        self._dice = Dice()

        with open("conf/conditions.yaml", "rb") as stream:
            try:
                self.conditions = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def get_status(player):
        """ check what condition your condition is in"""
        status = ""
        statuses = []
        for condition in player["conditions"]:
            if condition["condition"] not in "healthy":
                statuses.append(condition["condition"])

        statuses = list(set(statuses))

        if not statuses:
            status = "Healthy"

        elif len(statuses) == 1:
            status = statuses[0].capitalize()

        elif len(statuses) == 2:
            status = f"{statuses[0]} and {statuses[1]}".capitalize()

        else:
            status = f"{', '.join(statuses[:-1])} and {statuses[-1]}".capitalize()

        return status

    def get_condition_handle(self, name):
        """ return an array that corresponds to the named condition """
        condition = []

        for condition in self.conditions:
            if name in condition["type"]:
                return condition

        return condition

    def set_condition(self, name):
        """ add a condition to the list """
        condition = self.get_condition_handle(name).copy()
        condition["start"] = time.time()

        return condition

    def initialize_conditions(self, player):
        """
            start a new player with fatigue and make sure they are not
            hungry or thirsty
        """
        # check fatigue
        if player["class"] is None:
            return

        player["conditions"].append(self.set_condition("fatigued"))
        player["conditions"].append(self.set_condition("hungry"))
        player["conditions"].append(self.set_condition("thirsty"))

    def check_condition(self, player):
        """ check what condition your condition is in"""
        conditions = []

        # if new player skip check
        if player["class"] is None:
            return

        for condition in player["conditions"]:
            if condition["repeating"]:
                if time.time() - condition["start"] > condition["duration"]:
                    condition["condition"] = condition["type"]
                    conditions.append(condition)
                    if 'damage' in condition.keys():
                        if time.time() - condition["update"] > 6:
                            print("damaging repeating condition")
                            player["current_hp"] -= self._dice.roll(
                                condition["damage"])
                            condition["update"] = time.time()
                else:
                    conditions.append(condition)
            else:
                if time.time() - condition["start"] < condition["duration"]:
                    if 'damage' in condition.keys():
                        if time.time() - condition["update"] > 6:
                            print("damaging condition")
                            player["current_hp"] -= self._dice.roll(
                                condition["damage"])
                            condition["update"] = time.time()
                    conditions.append(condition)

        player["conditions"] = conditions
        player["status"] = self.get_status(player)
