""" magic class """
import yaml


class Magic():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self, mud=None):
        """ read in the config files """
        self._mud = mud

        with open("conf/magics.yaml", "rb") as stream:
            try:
                self.magics = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.levels = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # spell level
            [3, 2, 0, 0, 0, 0, 0, 0, 0, 0],  # lvl 1
            [3, 3, 0, 0, 0, 0, 0, 0, 0, 0],  # lvl 2
            [3, 4, 2, 0, 0, 0, 0, 0, 0, 0],  # lvl 3
            [4, 4, 3, 0, 0, 0, 0, 0, 0, 0],  # lvl 4
            [4, 4, 3, 2, 0, 0, 0, 0, 0, 0],  # lvl 5
            [4, 4, 3, 3, 0, 0, 0, 0, 0, 0],  # lvl 6
            [4, 4, 3, 3, 1, 0, 0, 0, 0, 0],  # lvl 7
            [4, 4, 3, 3, 2, 0, 0, 0, 0, 0],  # lvl 8
            [4, 4, 3, 3, 3, 1, 0, 0, 0, 0],  # lvl 9
            [5, 4, 3, 3, 3, 2, 0, 0, 0, 0],  # lvl 10
            [5, 4, 3, 3, 3, 2, 1, 0, 0, 0],  # lvl 11
            [5, 4, 3, 3, 3, 2, 1, 0, 0, 0],  # lvl 12
            [5, 4, 3, 3, 3, 2, 1, 1, 0, 0],  # lvl 13
            [5, 4, 3, 3, 3, 2, 1, 1, 0, 0],  # lvl 14
            [5, 4, 3, 3, 3, 2, 1, 1, 1, 0],  # lvl 15
            [5, 4, 3, 3, 3, 2, 1, 1, 1, 0],  # lvl 16
            [5, 4, 3, 3, 3, 2, 1, 1, 1, 1],  # lvl 17
            [5, 4, 3, 3, 3, 3, 1, 1, 1, 1],  # lvl 18
            [5, 4, 3, 3, 3, 3, 2, 1, 1, 1],  # lvl 19
            [5, 4, 3, 3, 3, 3, 2, 2, 1, 1],  # lvl 20
        ]

    def look_at_spellbook(self, uid, spellbook):
        """ list items if that room has them """
        self._mud.send_message(uid, "")
        self._mud.send_message(uid, "+======================+========+")
        self._mud.send_message(uid, "| Spell                | Level  |")
        self._mud.send_message(uid, "+----------------------+--------+")

        for item in sorted(spellbook["spells"], key=lambda x: x['level']):
            self._mud.send_message(
                uid, f"| {item['name']:20} | {item['level']:6} |")
        self._mud.send_message(uid, "+======================+========+")
