""" monsters class """
import time

import yaml


class Monster():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/monsters.yaml", "rb") as stream:
            try:
                self.mm = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.challenge = (
            25, 50, 100, 150, 200, 450, 700, 1100, 1800, 2300, 2900, 3900, 5000,
            5900, 7200, 8400, 10000, 11500, 13500, 18000, 20000, 22000, 25000,
            33000, 41000, 50000, 62000, 75000, 90000, 105000, 120000, 135000,
            155000
        )

        self.populate = time.time()
        self.spawn_timer = time.time()
