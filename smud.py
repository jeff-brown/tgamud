#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

Some ideas for things to try adding:
    * More rooms to explore
    * An 'emote' command e.g. 'emote laughs out loud' -> 'Mark laughs
        out loud'
    * A 'whisper' command for talking to individual players
    * A 'shout' command for yelling to players in all rooms
    * Items to look at in rooms e.g. 'look fireplace' -> 'You see a
        roaring, glowing fire'
    * Items to pick up e.g. 'take rock' -> 'You pick up the rock'
    * Monsters to fight
    * Loot to collect
    * Saving players accounts between sessions
    * A password login
    * A shop from which to buy items

Game Loop:

0. setup up global dicts (rooms, commands, players)
1. infinite Loop (while true)
2. call update to check for new socket events (mud.update())
3. check for new players (mud.get_new_players())
4. check for disconnected players (mud.get_disconnected_players())
5. check for new commands (mud.get_commands())
6. if not new player then do commands

Stuff to do:
    * player stats per class
    * implement magic system
    ! implement items
    ! implement stores
    * monster stat blocks per monster type / CR
    * monsters drop items / gold
    * more levels
    * implement lairs and wandering monsters
    ! fill in details for current rooms
    * monsters can equip stuff (pick stuff up too?)
    * implement other conditions (hungry, thirsty, poisoned, etc)
    * implement environment hazards: doors, traps, etc
    * fix pronoun and plural agreement (grammar, basically)
    * add ColOrS!1!!
    * implement character save and restore
    * darkness / light
    * day / night cycle? short / long rest?
    * quests?!
    * runes

author: Mark Frimston - mfrimston@gmail.com
"""

import random
import sys
import time

# import library objects
from lib.monster import Monster
from lib.room import Room
from lib.armor import Armor
from lib.weapon import Weapon
from lib.classes import Classes
from lib.species import Species
from lib.monsterstats import MonsterStats

# import the MUD server class
from server.mud import Mud


class Game():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self, mud):
        # start the server

        _monster = Monster()

        _room = Room()

        _armor = Armor()

        _weapon = Weapon()

        _classes = Classes()

        _species = Species()

        _monsterstats = MonsterStats()

        self._grid = [
            [0,  0,  0,  0,  0],
            [0,  0,  1,  0,  0],
            [0,  10, 2,  11, 0],
            [0,  0,  12, 0,  0],
            [0,  9,  3,  8,  0],
            [0,  0,  12, 0,  0],
            [0,  6,  4,  7,  0],
            [0,  0,  5,  0,  0],
            [0,  0,  0,  0,  0]
        ]

        self._modifiers = {
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

        self._cr = (25, 50, 100, 150, 200, 450, 700, 1100, 1800, 2300, 2900, 3900, 5000,
                    5900, 7200, 8400, 10000, 11500, 13500, 18000, 20000, 22000,
                    25000, 33000, 41000, 50000, 62000, 75000, 90000, 105000,
                    120000, 135000, 155000)

        self._classes = _classes.classes

        self._species = _species.species

        self._rooms = _room.rooms

        self._mm = _monster.mm

        self._monsterstats = _monsterstats.monsterstats

        self._weapons = _weapon.weapons

        self._armors = _armor.armors

        self._mud = mud

        self._players = {}

        self._monsters = {}

        self._exits = ["north", "south", "east", "west"]

        self._tick = 6  # 6 seconds

        # counter for assigning each client a new id
        self._nextid = 0

    @staticmethod
    def _d4():
        """
        roll a d4
        """
        return random.randint(1, 4)

    @staticmethod
    def _d6():
        """
        roll a d6
        """
        return random.randint(1, 6)

    @staticmethod
    def _d8():
        """
        roll a d8
        """
        return random.randint(1, 8)

    @staticmethod
    def _d10():
        """
        roll a d10
        """
        return random.randint(1, 10)

    @staticmethod
    def _d12():
        """
        roll a d12
        """
        return random.randint(1, 12)

    @staticmethod
    def _d20():
        """
        roll a d20
        """
        return random.randint(1, 20)

    @staticmethod
    def _d100():
        """
        roll a d100
        """
        return random.randint(1, 100)

    @staticmethod
    def _rdiv(num, div):
        """
        format coins
        """
        return num // div, num % div

    @staticmethod
    def _get_inventory(items):
        """
        output current level and experience
        """
        # check fatigue
        inventory = []
        for item in items:
            inventory.append(item["type"])

        if not inventory:
            return "You aren't carrying anything."

        if len(inventory) == 1:
            return f"You are carrying a {inventory[0]}."

        if len(inventory) == 2:
            return f"You are carrying a {inventory[0]} and a {inventory[1]}."

        return f"You are carrying {', '.join(inventory[:-1])} and a {inventory[-1]}."

    def _format_coins(self, coins):
        """
        format coins
        """
        wallet = []
        print(coins)
        plat, rem = self._rdiv(coins, 1000)
        if plat > 0:
            wallet.append(f"{int(plat)}p")
        print(plat, rem)
        gold, rem = self._rdiv(rem, 100)
        if gold > 0:
            wallet.append(f"{int(gold)}g")
        print(gold, rem)
        silv, rem = self._rdiv(rem, 10)
        if silv > 0:
            wallet.append(f"{int(silv)}s")
        print(silv, rem)
        copp, rem = self._rdiv(rem, 1)
        if copp > 0:
            wallet.append(f"{int(copp)}c")
        print(copp, rem)

        return " ".join(wallet)

    def _get_modifier(self, value):
        """get modifier"""
        for scores, modifer in self._modifiers.items():
            if value in scores:
                return modifer
        return value

    def _get_stat(self, uid, stat):
        """calculate stat with species bonuses"""
        print(type(uid))
        print(type(self._players[uid]["class"]))
        print(type(self._players[uid]["species"]))
        return self._classes[self._players[uid]["class"]][stat] \
            + self._species[self._players[uid]["species"]][stat]

    def _roll_dice(self, dice):
        """ roll the dice"""
        score = 0
        if dice[1] == 4:
            score = self._d4() * dice[0]
        elif dice[1] == 6:
            score = self._d6() * dice[0]
        elif dice[1] == 8:
            score = self._d8() * dice[0]
        elif dice[1] == 10:
            score = self._d10() * dice[0]
        elif dice[1] == 12:
            score = self._d12() * dice[0]
        elif dice[1] == 20:
            score = self._d20() * dice[0]
        elif dice[1] == 100:
            score = self._d100() * dice[0]
        return score

    def _max_enc(self, uid):
        """determind max hp"""
        return self._players[uid]["strength"] * 15

    def _cur_enc(self, uid):
        """determind max hp"""
        cur_enc = 0
        for item in self._players[uid]["inventory"]:
            cur_enc += item["weight"]

        return cur_enc

    def _max_hp(self, uid):
        """determind max hp"""
        return self._players[uid]["hit_dice"][1] \
            * self._players[uid]["hit_dice"][0] \
            + self._get_modifier(self._players[uid]["constitution"])

    def _monster_max_hp(self, uid):
        """determind max hp"""
        return self._monsters[uid]["hit_dice"][1] \
            * self._monsters[uid]["hit_dice"][0] \
            + self._get_modifier(self._monsters[uid]["constitution"])

    def _armor_class(self, uid):
        """determine ac"""
        if self._players[uid]["equipped"]["armor"]["size"] in ["light"]:
            return self._players[uid]["equipped"]["armor"]["ac"] + \
                self._get_modifier(self._players[uid]["dexterity"])
        if self._players[uid]["equipped"]["armor"]["size"] in ["medium"]:
            modifier = self._get_modifier(self._players[uid]["dexterity"])
            return self._players[uid]["equipped"]["armor"]["ac"] + \
                modifier if modifier < 3 else 2
        return self._players[uid]["equipped"]["armor"]["ac"]

    def _monster_armor_class(self, uid):
        """determine ac"""
        print(self._monsters[uid])
        if self._monsters[uid]["equipped"]["armor"]["size"] in ["light"]:
            return self._monsters[uid]["equipped"]["armor"]["ac"] + \
                self._get_modifier(self._monsters[uid]["dexterity"])
        if self._monsters[uid]["equipped"]["armor"]["size"] in ["medium"]:
            modifier = self._get_modifier(self._monsters[uid]["dexterity"])
            return self._monsters[uid]["equipped"]["armor"]["ac"] + \
                modifier if modifier < 3 else 2
        return self._monsters[uid]["equipped"]["armor"]["ac"]

    def _movement(self, uid):
        """
        return current room and possible exits
        """
        exits = []
        room = None

        x_coord = self._players[uid]["room"][0]
        y_coord = self._players[uid]["room"][1]

        room = self._grid[x_coord][y_coord]
        print("{}'s current loc [{},{}] in {}.".format(
            self._players[uid]["name"],
            x_coord, y_coord, self._rooms[room]["short"]))
        if self._grid[x_coord - 1][y_coord] > 0:
            exits.append("north")
        if self._grid[x_coord + 1][y_coord] > 0:
            exits.append("south")
        if self._grid[x_coord][y_coord - 1] > 0:
            exits.append("west")
        if self._grid[x_coord][y_coord + 1] > 0:
            exits.append("east")

        return room, exits

    def _get_hurt(self, mid):
        """ figure out how wounded a monster is """
        perc = (self._monsters[mid]["current_hp"]
                / float(self._monsters[mid]["max_hp"]) * 100)
        # healthy 85 - 100
        if 85 < perc < 100:
            status = "in good physical health"
        # light 61 - 84
        elif 61 < perc < 84:
            status = "lightly wounded"
        # wounded 41 - 60
        elif 41 < perc < 60:
            status = "wounded"
        # moderate 25 - 40
        elif 25 < perc < 40:
            status = "moderately wounded"
        # severe 1 - 24
        else:
            status = "severely wounded"

        return status

    def _process_look_at_command(self, uid, params):
        """look at stuff"""

        current_room, valid_exits = self._movement(uid)

        # look at _rooms
        if params == "room":
            self._mud.send_message(uid, self._rooms[current_room]["long"])
            return True

        # look outside the room
        if params in self._exits:
            if params in valid_exits:
                x_coord = self._players[uid]["room"][0]
                y_coord = self._players[uid]["room"][1]
                if params == "east":
                    next_room = self._grid[x_coord][y_coord + 1]
                elif params == "west":
                    next_room = self._grid[x_coord][y_coord - 1]
                elif params == "north":
                    next_room = self._grid[x_coord - 1][y_coord]
                elif params == "south":
                    next_room = self._grid[x_coord + 1][y_coord]
                self._mud.send_message(uid, self._rooms[next_room]["long"])
            else:
                self._mud.send_message(
                    uid, "You can see anything to the {}.".format(params))
            return True

        # look at monsters
        monsters_here = []
        for mid, monster in self._monsters.items():
            if monster["room"] == self._players[uid]["room"]:
                monsters_here.append(monster["name"])
            print(params)
            print(monsters_here)
            for monster_here in list(set(monsters_here)):
                if params in monster_here:
                    desc = (
                        [x["long"] for x in self._mm if x["name"] == monster_here]
                    )
                    hurt = self._get_hurt(mid)
                    self._mud.send_message(
                        uid, (desc[0] + " The {} appears to be {}.".format(
                            monster["name"], hurt)))
                else:
                    self._mud.send_message(
                        uid, "You don't see {} nearby.".format(params))
                return True

    def _process_look_command(self, uid):
        """
        write out the room and any players or items in it
        """
        room, exits = self._movement(uid)

        players_here = []
        monsters_here = []
        # go through every player in the game
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["room"] == self._players[uid]["room"] and \
                    pid != uid:
                # ... and they have a name to be shown
                if player["name"] is not None:
                    # add their name to the list
                    players_here.append(player["name"])

        for _, monster in self._monsters.items():
            if monster["room"] == self._players[uid]["room"]:
                monsters_here.append(monster["name"])

        # send player a message containing the list of players in the room
        if players_here:
            who = "{} are here with you.".format(", ".join(players_here))
        else:
            who = "There is nobody here."

        if monsters_here:
            if len(monsters_here) > 1:
                monster_line = (
                    "There is a {} here".format(", and a ".join(
                        monsters_here)))
            else:
                monster_line = "There is a {} here.".format(monsters_here[0])

        self._mud.send_message(uid, self._rooms[room]["short"])

        # this logic is tortured.  fix it later
        if monsters_here:
            self._mud.send_message(uid, monster_line)
        if players_here and monsters_here or players_here \
                and not monsters_here:
            self._mud.send_message(uid, who)
        elif not players_here and not monsters_here:
            self._mud.send_message(uid, who)
        self._mud.send_message(uid, "You can go {}.".format(", ".join(exits)))

    def _process_help_command(self, uid):
        """
        write out the room and any players or items in it
        """
        self._mud.send_message(uid, "Commands:")
        self._mud.send_message(
            uid, "  say <message>  - Says something out loud.")
        self._mud.send_message(
            uid, "  look           - Examines the surroundings")
        self._mud.send_message(
            uid, "  go <exit>      - Moves through the exit specified.")
        self._mud.send_message(
            uid, "  quit           - Quits the game.")

    def _process_new_player(self, uid, command):
        """
        add a new players name to the dictionary and stick them in a room
        """
        self._players[uid]["class"] = command
        self._players[uid]["rune"] = "None"
        self._players[uid]["room"] = [4, 2]
        self._players[uid]["fatigue"] = time.time()
        self._players[uid]["hit_dice"] = self._classes[command]["hit_dice"]
        self._players[uid]["level"] = 1
        self._players[uid]["strength"] = self._get_stat(uid, "strength")
        self._players[uid]["dexterity"] = self._get_stat(uid, "dexterity")
        self._players[uid]["constitution"] = self._get_stat(uid, "constitution")
        self._players[uid]["intelligence"] = self._get_stat(uid, "intelligence")
        self._players[uid]["wisdom"] = self._get_stat(uid, "wisdom")
        self._players[uid]["charisma"] = self._get_stat(uid, "charisma")
        self._players[uid]["max_hp"] = self._max_hp(uid)
        self._players[uid]["current_hp"] = self._max_hp(uid)
        self._players[uid]["regen_hp"] = time.time()
        self._players[uid]["max_mp"] = 0
        self._players[uid]["current_mp"] = 0
        self._players[uid]["max_enc"] = self._max_enc(uid)
        self._players[uid]["current_enc"] = 0
        self._players[uid]["xp"] = 0
        self._players[uid]["level"] = 1
        self._players[uid]["status"] = "Healthy"
        self._players[uid]["equipped"] = {
            "weapon": self._weapons[0],
            "armor": self._armors[0]
        }
        self._players[uid]["armor_class"] = self._armor_class(uid)
        self._players[uid]["inventory"] = []
<<<<<<< HEAD
        self._players[uid]["coins"] = (
            self._roll_dice(self._classes[command]["wealth"])
            * self._classes[command]["wealth"][2]
        )
=======
        self._players[uid]["coins"] = 2 * self._d4() * random.randint(951, 999)
        print(self._players)
>>>>>>> ee5cd5226b9e56ce3df5f605968d086c4dcc921c

        # go through all the players in the game
        for pid, _ in self._players.items():
            # send each player a message to tell them about the new player
            if pid != uid:
                self._mud.send_message(pid, "{} entered the game".format(
                    self._players[uid]["name"]))

        # send the new player a welcome message
        self._mud.send_message(uid, "Welcome to the game, {}. ".format(
            self._players[uid]["name"]))

        # send the new player the description of their current room
        self._process_look_command(uid)

    def _process_say_command(self, uid, params):
        """
        say stuff to other folks
        """
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["room"] == self._players[uid]["room"] \
                    and pid != uid:
                # send them a message telling them what the player said
                self._mud.send_message(pid, "{} says: {}".format(
                    self._players[uid]["name"], params))

    def _process_quit_command(self, uid):
        """
        exit on your own terms
        """
        self._mud.send_message(uid, "Goodbye, {}.".format(
            self._players[uid]["name"]))
        self._mud.get_disconnect(uid)

    def _process_unequip_command(self, uid, params):
        """
        output current level and experience
        """
        player = self._players[uid]

        if not params:
            self._mud.send_message(
                uid, "You need to specify what you want to unequip.")
            return

        print(params, player["equipped"]["armor"]["type"])
        print(params, player["equipped"]["weapon"]["type"])
        if player["equipped"]["armor"] \
                and params in player["equipped"]["armor"]["type"]:
            self._mud.send_message(
                uid, (
                    f"You just unequipped "
                    f"{player['equipped']['armor']['type']}."
                )
            )
            self._players[uid]["inventory"].append(player['equipped']['armor'])
            self._players[uid]["equipped"]["armor"] = None

        elif player["equipped"]["weapon"] \
                and params in player['equipped']['weapon']['type']:
            self._mud.send_message(
                uid, (
                    f"You just unequipped "
                    f"{player['equipped']['weapon']['type']}."
                )
            )
            self._players[uid]["inventory"].append(player['equipped']['weapon'])
            self._players[uid]["equipped"]["weapon"] = None
        else:
            self._mud.send_message(
                uid, (
                    f"You don't seem to have {params} equipped."
                )
            )

    def _process_equip_command(self, uid, params):
        """
        output current level and experience
        """
        player = self._players[uid]

        if not params:
            self._mud.send_message(
                uid, "You need to specify what you want to equip.")
            return

        for item in player["inventory"]:
            if params in item["type"] and item["equip"]:
                if item["etype"] == "armor":
                    if player["equipped"]["armor"]:
                        self._process_unequip_command(
                            uid, player["equipped"]["armor"]["type"])
                    self._players[uid]["equipped"]["armor"] = item
                    self._players[uid]["armor_class"] = self._armor_class(uid)
                    self._players[uid]["inventory"].remove(item)
                    self._mud.send_message(uid, f"You equipped {item['type']}.")

                elif item["etype"] in ["one-hand", "two-hand"]:
                    if player["equipped"]["weapon"]:
                        self._process_unequip_command(
                            uid, player["equipped"]["weapon"]["type"])
                    self._players[uid]["equipped"]["weapon"] = item
                    self._players[uid]["inventory"].remove(item)
                    self._mud.send_message(uid, f"You equipped {item['type']}.")

                else:
                    self._mud.send_message(uid, f"You can't equip {params}.")

    def _process_experience_command(self, uid):
        """
        output current level and experience
        """
        self._mud.send_message(uid, "You have {} experience.".format(
            self._players[uid]["xp"]))

    def _process_ring_gong(self, uid):
        """
        output current level and experience
        """
        # check fatigue
        if len(self._monsters) < 9:
            self._spawn_monsters()
        else:
            print("rooms full")

    def _check_status(self, uid):
        """
        output current level and experience
        """
        # check fatigue
        if self._players[uid]["class"] is None:
            return

        if time.time() - self._players[uid]["fatigue"] < self._tick:
            self._players[uid]["status"] = "Fatigued"
        else:
            self._players[uid]["status"] = "Healthy"

    def _get_inventory(self, items):
        """
        output current level and experience
        """
        # check fatigue
        inventory = []
        for item in items:
            inventory.append(item["type"])

        if not inventory:
            return "You aren't carrying anything."

        if len(inventory) == 1:
            return f"You are carrying a {inventory[0]}."

        if len(inventory) == 2:
            return f"You are carrying a {inventory[0]} and a {inventory[1]}."

        return f"You are carrying {', '.join(inventory[:-1])} and a {inventory[-1]}."

    def _regenerate(self, uid):
        """
        output current level and experience
        """
        if self._players[uid]["class"] is None:
            return

        # regen_hp
        if time.time() - self._players[uid]["regen_hp"] > self._tick:
            self._players[uid]["current_hp"] += self._d4()
            self._players[uid]["regen_hp"] = time.time()
            if self._players[uid]["current_hp"] > self._players[uid]["max_hp"]:
                self._players[uid]["current_hp"] = self._players[uid]["max_hp"]

    def _process_inv_command(self, uid):
        """
        output current level and experience
        """
        self._mud.send_message(uid, "")
        self._mud.send_message(
            uid, self._get_inventory(self._players[uid]["inventory"]))

    def _process_stats_command(self, uid):
        """
        output current level and experience
        """
        self._mud.send_message(uid, "Name:         {}".format(
            self._players[uid]["name"]))
        self._mud.send_message(uid, "Species:      {}".format(
            self._species[self._players[uid]["species"]]["type"]))
        self._mud.send_message(uid, "Class:        {}".format(
            self._classes[self._players[uid]["class"]]["type"]))
        self._mud.send_message(uid, "Level:        {}".format(
            self._players[uid]["level"]))
        self._mud.send_message(uid, "Experience:   {}".format(
            self._players[uid]["xp"]))
        self._mud.send_message(uid, "Rune:         {}".format(
            self._players[uid]["rune"]))
        self._mud.send_message(uid, "")
        self._mud.send_message(uid, "Intelligence: {}".format(
            self._players[uid]["intelligence"]))
        self._mud.send_message(uid, "Wisdom:       {}".format(
            self._players[uid]["wisdom"]))
        self._mud.send_message(uid, "Strength:     {}".format(
            self._players[uid]["strength"]))
        self._mud.send_message(uid, "Constitution: {}".format(
            self._players[uid]["constitution"]))
        self._mud.send_message(uid, "Dexterity:    {}".format(
            self._players[uid]["dexterity"]))
        self._mud.send_message(uid, "Charisma:     {}".format(
            self._players[uid]["charisma"]))
        self._mud.send_message(uid, "")
        self._mud.send_message(uid, "Mana:         {} / {}".format(
            self._players[uid]["current_mp"], self._players[uid]["max_mp"]))
        self._mud.send_message(uid, "Hit Points:   {} / {}".format(
            self._players[uid]["current_hp"], self._players[uid]["max_hp"]))
        self._mud.send_message(uid, "Status:       {}".format(
            self._players[uid]["status"]))
        self._mud.send_message(uid, "Armor Class:  {}".format(
            self._players[uid]["armor_class"]))
        self._mud.send_message(uid, "")
        self._mud.send_message(uid, "Weapon:       {}".format(
            self._players[uid]["equipped"]["weapon"]["type"]))
        self._mud.send_message(uid, "Armor:        {}".format(
            self._players[uid]["equipped"]["armor"]["type"]))
        self._mud.send_message(uid, "Coins:        {}".format(
            self._format_coins(self._players[uid]["coins"])))
        self._mud.send_message(uid, "Encumberance: {} / {} lbs".format(
            self._cur_enc(uid), self._players[uid]["max_enc"]))
        self._mud.send_message(uid, "Inventory:    {}".format(
            self._get_inventory(self._players[uid]["inventory"])))

    def _process_health_command(self, uid):
        """
        output current level and experience
        """
        self._mud.send_message(uid, "Magic Points: {} / {}".format(
            self._players[uid]["current_mp"], self._players[uid]["max_mp"]))
        self._mud.send_message(uid, "Hit Points:   {} / {}".format(
            self._players[uid]["current_hp"], self._players[uid]["max_hp"]))
        self._mud.send_message(uid, "Status:       {}".format(
            self._players[uid]["status"]))

    def _process_go_command(self, uid, command, params):
        """
        move around
        """
        if time.time() - self._players[uid]["fatigue"] < self._tick:
            self._mud.send_message(
                uid, (
                    "Sorry, you'll have to rest a while before you can move."
                )
            )
            return

        # get the exit and store it
        if command == "go":
            door = params.lower()
        else:
            door = command.lower()

        # get current room and list of exits
        _, exits = self._movement(uid)

        # if the specified exit is found in the room's exits list
        if door in exits:

            # go through all the players in the game
            for pid, player in self._players.items():
                # if player is in the same room and isn't the player
                # sending the command
                if player["room"] == self._players[uid]["room"] \
                        and pid != uid:
                    # send them a message telling them that the player
                    # left the room
                    self._mud.send_message(
                        pid, "{} just left to the {}.".format(
                            self._players[uid]["name"], door))

            # update the player's current room to the one the exit leads to
            if door == "south":
                self._players[uid]["room"][0] += 1
            if door == "north":
                self._players[uid]["room"][0] -= 1
            if door == "east":
                self._players[uid]["room"][1] += 1
            if door == "west":
                self._players[uid]["room"][1] -= 1

            # go through all the players in the game
            for pid, player in self._players.items():
                # if player is in the same (new) room and isn't the player
                # sending the command
                if player["room"] == self._players[uid]["room"] \
                        and pid != uid:
                    # send them a message telling them that the player
                    # entered the room
                    self._mud.send_message(
                        pid, "{} just arrived from the {}.".format(
                            self._players[uid]["name"], door))

            # send the player a message telling them where they are now
            self._process_look_command(uid)

        # the specified exit wasn't found in the current room
        else:
            # send back an 'unknown exit' message
            self._mud.send_message(
                uid, "A mysterious force blocks your path to the {}.".format(
                    door))

    def _process_attack_command(self, uid, params):
        """
        try to kill some stuff why not
        """
        player = self._players[uid]
        monsters = self._monsters.copy()

        for mid, monster in monsters    .items():
            if params in monster["name"] and monster["room"] \
                    == self._players[uid]["room"]:
                if time.time() - self._players[uid]["fatigue"] > self._tick:
                    attack = (
                        self._d20() + self._get_modifier(player["strength"]))
                    print("max hp: {}".format(monster["max_hp"]))
                    print("cur hp: {}".format(monster["current_hp"]))
                    print("")
                    print("attack: {}".format(attack))
                    print("monster ac: {}".format(monster["armor_class"]))
                    xp_incr = int(self._cr[monster["cr"]] / monster["max_hp"])
                    if attack > monster["armor_class"]:
                        dice = (
                            self._roll_dice(
                                player["equipped"]["weapon"]["damage"]
                            )
                        )
                        damage = dice + self._get_modifier(player["strength"])
                        self._mud.send_message(
                            uid,
                            "Your attack hits {} for {} damage.".format(
                                monster["name"], damage))
                        monster["current_hp"] -= damage
                        self._players[uid]["xp"] += xp_incr * damage
                        if monster["current_hp"] < 1:
                            del self._monsters[mid]
                            self._mud.send_message(
                                uid,
                                (
                                    "The {} falls to the ground "
                                    "lifeless!".format(monster["name"])
                                )
                            )
                            self._players[uid]["coins"] += monster["coins"]
                            self._mud.send_message(
                                uid,
                                (
                                    "You found {} gold crowns while searching "
                                    "the {}'s corpse.".format(
                                        self._format_coins(monster["coins"]),
                                        monster["name"]
                                    )
                                )
                            )
                        self._players[uid]["fatigue"] = time.time()
                    else:
                        self._mud.send_message(
                            uid, (
                                "Your poorly executed attacked misses "
                                "the {}.".format(monster["name"])
                            )
                        )
                        self._players[uid]["fatigue"] = time.time()
                else:
                    self._mud.send_message(
                        uid, (
                            "You are still physically exhausted from your "
                            "previous activities!"
                        )
                    )
            else:
                self._mud.send_message(
                    uid, "Sorry, you don't see '{}' nearby.".format(params))

    def _spawn_monsters(self):
        """
        check lairs and spawn monsters if they are empty
        """
        self._monsters[self._nextid] = (
            random.choice([x for x in self._mm if x["cr"] < 2])
        )
        self._monsters[self._nextid]["room"] = [4, 3]
        print(self._monsters[self._nextid])
        print(self._monsterstats[self._monsters[self._nextid]["cr"]]["hit_dice"])
        self._monsters[self._nextid]["hit_dice"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["hit_dice"]
        )
        self._monsters[self._nextid]["fatigue"] = time.time()
        self._monsters[self._nextid]["strength"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["strength"]
        )
        self._monsters[self._nextid]["dexterity"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["dexterity"]
        )
        self._monsters[self._nextid]["constitution"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["constitution"]
        )
        self._monsters[self._nextid]["intelligence"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["intelligence"]
        )
        self._monsters[self._nextid]["wisdom"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["wisdom"]
        )
        self._monsters[self._nextid]["charisma"] = (
            self._monsterstats[self._monsters[self._nextid]["cr"]]["charisma"]
        )
        self._monsters[self._nextid]["max_hp"] = (
            self._monster_max_hp(self._nextid))
        self._monsters[self._nextid]["current_hp"] = (
            self._monster_max_hp(self._nextid))
        self._monsters[self._nextid]["equipped"] = {
            "weapon": self._weapons[0],
            "armor": self._armors[0]
        }
        self._monsters[self._nextid]["armor_class"] = (
            self._monster_armor_class(self._nextid)
        )
        self._monsters[self._nextid]["regen_hp"] = time.time()
        self._monsters[self._nextid]["armor_class"] = (
            self._monster_armor_class(self._nextid))
        self._monsters[self._nextid]["coins"] = self._roll_dice([1, 4]) * 100
        print(
            "spawned {} with cr {} that has {} xp.".format(
                self._monsters[self._nextid]["name"],
                self._monsters[self._nextid]["cr"],
                self._cr[self._monsters[self._nextid]["cr"]]
            )
        )

        for pid, player in self._players.items():
            if self._monsters[self._nextid]["room"] == player["room"]:
                self._mud.send_message(
                    pid, (
                        "A {} just appeared in a blinding flash of "
                        "light.".format(self._monsters[self._nextid]["name"])
                    )
                )
        self._nextid += 1

    def _monsters_move(self):
        """
        if monsters aren't tethered to a lair, move them around
        """

    def _monsters_attack(self, mid):
        """
        monsters always attack if they are able.  beware.
        """
        monster = self._monsters[mid]
        for pid, player in self._players.items():
            if player["room"] == monster["room"]:
                if time.time() - monster["fatigue"] > self._tick:

                    attack = (
                        self._d20()
                        + self._get_modifier(monster["strength"])
                    )
                    print("attack: {}".format(attack))
                    print("player ac: {}".format(player["armor_class"]))
                    if attack > player["armor_class"]:
                        dice = (
                            self._roll_dice(
                                monster["equipped"]["weapon"]["damage"]
                            )
                        )
                        damage = (
                            dice
                            + self._get_modifier(monster["strength"])
                        )
                        self._mud.send_message(
                            pid, (
                                "The {} attacked you with their {} for {} "
                                "damage!".format(
                                    monster["name"],
                                    monster["equipped"]["weapon"]["type"],
                                    damage))
                                )
                        player["current_hp"] -= damage
                        if player["current_hp"] < 1:
                            self._mud.send_message(pid, (
                                "As the final blow strikes your body you "
                                "fall unconscious."))
                            self._mud.send_message(pid, (
                                "You awaken after an unknown amount of "
                                "time..."))
                            self._players[pid]["room"] = [4, 2]
                            self._players[pid]["current_hp"] = 1
                            self._process_look_command(pid)
                        # del self._monsters[mid]
                        self._monsters[mid]["fatigue"] = time.time()
                    else:
                        self._mud.send_message(
                            pid, (
                                "The {}'s poorly executed attacked misses "
                                "you.".format(monster["name"])
                            )
                        )
                        self._monsters[mid]["fatigue"] = time.time()

    def _process_list_command(self, uid):
        """ list items if that room has them """
        current_room, _ = self._movement(uid)

        print(self._rooms[current_room])

        if "items" in self._rooms[current_room].keys():

            self._mud.send_message(uid, "")
            self._mud.send_message(uid, "+======================+========+")
            self._mud.send_message(uid, "| Item                 | Price  |")
            self._mud.send_message(uid, "+----------------------+--------+")
            for item in self._rooms[current_room]["items"]:
                self._mud.send_message(
                    uid, (
                        f"| {item['type']:21}"
                        f"| {self._format_coins(item['value']):7}|"
                    )
                )
            self._mud.send_message(uid, "+======================+========+")

        else:
            self._mud.send_message(
                uid, "Sorry, that is not an appropriate command.")

    def _process_buy_command(self, uid, params):
        """ list items if that room has them """
        current_room, _ = self._movement(uid)
        merch = None

        if "items" in self._rooms[current_room].keys():
            for item in self._rooms[current_room]["items"]:
                if params in item["type"]:
                    merch = item

            if merch:
                print(f"merch: {merch}")
                if self._players[uid]["coins"] > merch["value"]:
                    if merch["inv"]:
                        self._players[uid]["inventory"].append(merch)
                    self._players[uid]["coins"] -= merch["value"]
                    self._mud.send_message(
                        uid, (
                            f"You just purchased {merch['type']} for "
                            f"{self._format_coins(merch['value'])}."
                        )
                    )
                else:
                    self._mud.send_message(
                        uid, f"You can't afford {merch['type']}.")
            else:
                self._mud.send_message(
                    uid, f"This shop doesn't offer {params}.")

    def check_for_new_players(self):
        """
        check to see if any new connections arrived since last update
        """
        # go through any newly connected players
        for pid in self._mud.get_new_players():

            # add the new player to the dictionary, noting that they've not
            # named yet.
            # The dictionary key is the player's id number. We set their room
            # None initially until they have entered a name
            # Try adding more player stats - level, gold, inventory, etc
            self._players[pid] = {
                "name": None,
                "species": None,
                "class": None,
                "room": None
            }

            # send the new player a prompt for their name
            self._mud.send_message(pid, "What is your name?")

    def check_for_disconnected_players(self):
        """
        check to see if anyone disconnected since last update
        """
        for uid in self._mud.get_disconnected_players():

            # if for any reason the player isn't in the player map, skip them
            # move on to the next one
            if uid not in self._players:
                continue

            # go through all the players in the game
            for pid, _ in self._players.items():
                # send each player a message to tell them about the diconnected
                # player
                if pid != uid:
                    self._mud.send_message(pid, "{} quit the game".format(
                        self._players[uid]["name"]))

            # remove the player's entry in the player dictionary
            del self._players[uid]

    def check_for_new_commands(self):
        """
        check to see if any new commands are on the queue
        """
        for uid, command, params in self._mud.get_commands():

            # if for any reason the player isn't in the player map, skip them
            # move on to the next one
            if uid not in self._players:
                continue

            # if the player hasn't given their name yet, use this first command
            # their name and move them to the starting room.
            if self._players[uid]["name"] is None:

                self._players[uid]["name"] = command

                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "| Num      | Species    |")
                self._mud.send_message(uid, "+----------+------------+")
                for num, species in enumerate(self._species):
                    self._mud.send_message(
                        uid, (
                            f"| {num:<9}"
                            f"| {species['type']:11}|"
                        )
                    )
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "What species are you?")

            elif self._players[uid]["species"] is None:

                self._players[uid]["species"] = int(command)

                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "| Num      | Class      |")
                self._mud.send_message(uid, "+----------+------------+")
                for num, classes in enumerate(self._classes):
                    self._mud.send_message(
                        uid, (
                            f"| {num:<9}"
                            f"| {classes['type']:11}|"
                        )
                    )
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "What class are you?")

            elif self._players[uid]["class"] is None:

                self._process_new_player(uid, int(command))

            # 'help' command
            elif command == "help":

                # send the player back the list of possible commands
                self._process_help_command(uid)

            # 'say' command
            elif command == "say":

                # go through every player in the game
                self._process_say_command(uid, params)

            # 'look' command
            elif command in ["look", "l", ""]:

                # look around to see who and what is around
                if params == "":
                    self._process_look_command(uid)
                else:
                    self._process_look_at_command(uid, params)

            # 'go' command
            elif command in ["go", "east", "west", "north", "south"]:

                # go to another rooms
                self._process_go_command(uid, command, params)

            # "attack" command
            elif command in ["attack", "a"]:

                # let's gooooo
                self._process_attack_command(uid, params)

            elif command in ["experience", "xp"]:

                # let's gooooo
                self._process_experience_command(uid)

            elif command in ["stats", "st"]:

                # let's gooooo
                self._process_stats_command(uid)

            elif command in ["health", "hp"]:

                # let's gooooo
                self._process_health_command(uid)

            elif command in ["ring", "r"] and params in ["gong", "g"]:

                # let's gooooo
                self._process_ring_gong(uid)

            # 'list' command
            elif command == "list":

                # go to another rooms
                self._process_list_command(uid)

            # 'list' command
            elif command == "buy":

                # go to another rooms
                self._process_buy_command(uid, params)

            elif command == "inv":

                # go to another rooms
                self._process_inv_command(uid)

            elif command == "equip":

                # go to another rooms
                self._process_equip_command(uid, params)

            # 'exit' command
            elif command == "quit":

                # go to another rooms
                self._process_quit_command(uid)

            # some other, unrecognised command
            else:
                # send back an 'unknown command' message
                self._mud.send_message(
                    uid, "Unknown command '{}'".format(command))

    def check_for_monsters(self):
        """
        spawn monsters and move them around
        """
        # spawn rnd monster in arena if empty
        # self._spawn_monsters()

        for mid, _ in self._monsters.items():

            # monsters attack first and ask questions later
            self._monsters_attack(mid)

            # monsters wander if no one is around and run if they are injured
            self._monsters_move()

    def check_for_status(self):
        """
        spawn monsters and move them around
        """
        for pid, _ in self._players.items():

            if self._players[pid]["name"] is None:
                continue

            # monsters attack first and ask questions later
            self._check_status(pid)

            # monsters wander if no one is around and run if they are injured
            self._regenerate(pid)


def main():
    """
    function main
    args: none
    returns: none
    """

    # start the server
    mud = Mud()

    # create and instance of the game
    game = Game(mud)

    # main game loop. We loop forever (i.e. until the program is terminated)
    while True:

        # pause for 1/5 of a second on each loop, so that we don't constantly
        # use 100% CPU time
        time.sleep(0.2)

        # 'update' must be called in the loop to keep the game running and give
        # us up-to-date information
        mud.update()

        game.check_for_monsters()

        game.check_for_new_players()

        game.check_for_disconnected_players()

        game.check_for_new_commands()

        game.check_for_status()

    return 0


if __name__ == '__main__':
    sys.exit(main())
