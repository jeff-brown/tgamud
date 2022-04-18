""" condition class """
import time
import yaml

from lib.dice import Dice
from lib.gear import Gear


class Condition():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        self.conditions = []

        self._dice = Dice()

        self._gear = Gear()

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

    def remove_condition(self, player, name):
        """ add a condition to the list """
        for index, condition in enumerate(player["conditions"]):
            if condition["condition"] == name:
                if condition["repeating"]:
                    del player['conditions'][index]
                    player["conditions"].append(self.set_condition(name))
                else:
                    del player['conditions'][index]
                return True

        return False

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

    def eat(self, player, meal):
        """ eat a thing and see what happens """
        foods = [x for x in self._gear.gears if x['dtype'] == 'food']
        items = [x for x in player["inventory"] if x['dtype'] == 'food']
        conditions = self.get_status(player).lower()
        message = None

        print(foods)
        print([x['type'] for x in foods])
        print(items)
        print([x['type'] for x in items])
        print(meal)

        print(bool([x['type'] for x in foods if meal not in x['type']]))
        if [x['type'] for x in foods if meal not in x['type']]:
            return f"You can't eat {meal}!"

        print(bool([x['type'] for x in items if meal in x['type']]))
        if [x['type'] for x in items if meal not in x['type']] or not items:
            return f"You don't seem to have {meal}!"

        for item in items:
            if meal in item["type"]:
                print("found", meal)
                if item["effect"] in conditions:
                    print("found", item["effect"])
                    self.remove_condition(player, item["effect"])
                    message = item["message"].format(item["type"])
                else:
                    message = f"The {item['type']} seems to have no effect!"
                self._gear.remove_item(player, item['type'])
            else:
                message = f"You do not seem to have {meal}"

        return message

    def drink(self, player, bev):
        """ drink a thing and see what happens """
        if not player["inventory"]:
            return "You're not carrying anything."

        beverages = [x for x in self._gear.gears if x['dtype'] == 'beverage']
        items = [x for x in player["inventory"] if x['dtype'] == 'beverage']
        conditions = self.get_status(player).lower()
        message = None

        if [x['type'] for x in beverages if bev not in x['type']]:
            return f"You can't drink {bev}!"

        if [x['type'] for x in items if bev not in x['type']]:
            return f"You don't seem to have {bev}!"

        for item in items:
            if bev in item["type"]:
                print("found", bev)
                if item["effect"] in conditions:
                    print("found", item["effect"])
                    self.remove_condition(player, item["effect"])
                    message = item["message"].format(item["type"])
                else:
                    message = f"The {item['type']} seems to have no effect!"
                self._gear.remove_item(player, item['type'])
            else:
                message = f"You do not seem to have {bev}"

        return message

    @staticmethod
    def _process_heal(player, heal):
        """ process heal """
        player["current_hp"] += heal
        if player["current_hp"] > player["max_hp"]:
            player["current_hp"] = player["max_hp"]
        return None

    @staticmethod
    def heal_cost(player, cost):
        """ process heal """
        heal = player["max_hp"] - player["current_hp"]
        if heal > 0:
            return (player["max_hp"] - player["current_hp"]) * cost * player["level"]
        else:
            return 0

    def buy_heal(self, player):
        """ process heal """
        message = None
        heal = player["max_hp"] - player["current_hp"]
        if heal > 0:
            self._process_heal(player, heal)
            message = f"The priests healed your for {heal} hp."
        else:
            message = "You don't need healing!"

        return message
