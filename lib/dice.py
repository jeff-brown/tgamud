""" dice class """
import random


class Dice():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """

    @staticmethod
    def roll(dice):
        """ roll the dice"""
        score = 0
        for _ in range(dice[0]):
            score += random.randint(1, dice[1])

        if len(dice) > 2:
            return score + dice[2]
        return score
