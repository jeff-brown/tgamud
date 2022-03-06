""" Classes class """
import random

import yaml

from lib.dice import Dice

class Classes():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/classes.yaml", "rb") as stream:
            try:
                self.classes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self._dice = Dice()

        self.exp = [  # exp, lvl, pro
            (-1, 0, 0),
            (0, 1, 2),
            (300, 2, 2),
            (900, 3, 2),
            (2700, 4, 2),
            (6500, 5, 3),
            (14000, 6, 3),
            (23000, 7, 3),
            (34000, 8, 3),
            (48000, 9, 4),
            (64000, 10, 4),
            (85000, 11, 4),
            (100000, 12, 4),
            (120000, 13, 5),
            (140000, 14, 5),
            (165000, 15, 5),
            (195000, 16, 5),
            (225000, 17, 6),
            (265000, 18, 6),
            (305000, 19, 6),
            (355000, 20, 6)
        ]

        self.mod = {
            (0, 1): -5,
            (2, 3): -4,
            (4, 5): -3,
            (6, 7): -2,
            (8, 9): -1,
            (10, 11): 0,
            (12, 13): 1,
            (14, 15): 2,
            (16, 17): 3,
            (18, 19): 4,
            (20, 21): 5,
            (22, 23): 6,
            (24, 25): 7,
            (26, 27): 8,
            (28, 29): 9,
            (30, 31): 10
        }

        self.prof = {
            0: 1,
            1: 2,
            2: 2,
            3: 2,
            4: 2,
            5: 3,
            6: 3,
            7: 3,
            8: 3,
            9: 4,
            10: 4,
            11: 4,
            12: 4,
            13: 5,
            14: 5,
            15: 5,
            16: 5,
            17: 6,
            18: 6,
            19: 6,
            20: 6
        }

        self.abilities = ("strength", "constitution", "dexterity", "wisdom",
                          "charisma", "intelligence")

    def _get_modifier(self, value):
        """get modifier"""
        for scores, modifer in self.mod.items():
            if value in scores:
                return modifer
        return value

    def _max_hp(self, player):
        """determind max hp"""
        return player["max_hp"] \
            + self._dice.roll([1, player["hit_dice"][1]]) \
            + self._get_modifier(player["constitution"])

    def _ability_score_increase(self, player):
        """ randomly increase ability scores based on level """
        if player["level"] not in self.classes[player["class"]]["asi"]:
            return

        for _ in range(2):
            print(_)
            ability = random.choice(self.abilities)
            max_stats = []
            while True:
                if player[ability] < 20:
                    break
                max_stats.append(ability)
                if len(max_stats) is len(self.abilities):
                    break
                ability = random.choice(self.abilities)
            if len(max_stats) < len(self.abilities):
                player[ability] += 1

    def check_level(self, player):
        """ see if player can advance """
        if player["level"] == 20:
            return False

        if player["xp"] > self.exp[player["level"] + 1][0]:
            return True
        return False

    def level_up(self, player):
        """ level up a player to the next level """
        if self.check_level(player):

            # increment player level
            player["level"] += 1

            # increase proficiency based on level
            player["proficiency"] = self.exp[player["level"]][2]

            # increase ability scores if needed
            self._ability_score_increase(player)

            # add another hit dice
            player["hit_dice"][0] += 1

            # increment max_hp
            player["max_hp"] = self._max_hp(player)
