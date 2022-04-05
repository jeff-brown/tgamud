""" condition class """
import time
import yaml


class Condition():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        self.conditions = []

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

        print(statuses)

        if not statuses:
            status = "Healthy"

        elif len(statuses) == 1:
            status = statuses[0]

        elif len(statuses) == 2:
            status = f"{statuses[0]} and {statuses[1]}"

        else:
            status = f"{', '.join(statuses[:-1])} and {statuses[-1]}"

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

    @staticmethod
    def initialize_conditions(player):
        """
            start a new player with fatigue and make sure they are not
            hungry or thirsty
        """
        # check fatigue
        if player["class"] is None:
            return

        player["conditions"].append("fatigued")
        player["conditions"].append("hungry")
        player["conditions"].append("thirsty")

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
                else:
                    conditions.append(condition)
            else:
                if time.time() - condition["start"] < condition["duration"]:
                    conditions.append(condition)

        player["conditions"] = conditions
        player["status"] = self.get_status(player)
