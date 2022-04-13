""" weapon class """
import yaml


class Gear():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/gears.yaml", "rb") as stream:
            try:
                self.gears = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def remove_item(player, name):
        """ add a condition to the list """
        for index, gear in enumerate(player["inventory"]):
            if gear["type"] == name:
                if 'quantity' in gear.keys():
                    gear['quantity'] -= 1
                    if gear['quantity'] < 1:
                        del player['inventory'][index]
                else:
                    del player['inventory'][index]

                return True

        return False
