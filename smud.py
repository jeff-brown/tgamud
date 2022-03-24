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

Feature Requests:
     ! add ability to "cast" spells on players, mobs and items
     ! add ability to "learn" spells and add them to your spellbook
     ! add spells to shop for each class
     ! added leveling to Classes class
    ! can only equip if you are proficient
    ! encumberance needs to include equipped items
    ! fill in details for current rooms
    ! fix traveling between floors IMPORTANT game broken
    ! FIXIT need to use .copy() whenever assign items to characters/monsters
    ! implement buy/sell
    ! implement items
    ! implement player leveling system
    ! implement stores
      ! lairs done
    ! monster stat blocks per monster type / CR
    ! monsters attack monsters
    ! monsters can equip stuff
    ! monsters drop gold
    ! monsters drop items / get items
    ! more dungeons
    ! more items (weapons, armor, etc)
     ! need to be able to purchse leveling in guild hall
    ! darkness / light
    ! player stats per class
    * add ColOrS!1!!
    * alignment
    * all send_message commands need player and other_player text
    * can cheat by letting monsters fight

    * day / night cycle? short / long rest?
    * durability (and item properties)
    * fix pronoun and plural agreement (grammar, basically)
    * implement character save and restore
    * implement environment hazards: doors, traps, etc
    * implement wandering monsters
    * implement magic system
    * implement other conditions (hungry, thirsty, poisoned, etc)
    * look at players,
    * monsters pick stuff up too?)
    * need a way to travel between dungeons (teleporter)
    * need npcs - they have stat blocks and alignments
    * need to have level restrictions on equipment (monsters too)
    * pvp?
    * quests?!
    * runes
    * temporary stats - each stat needs temp and perm
     - cantrips must be added to spell slots and can only be cast once before a rest
     - charisma needs to influence buy/sell price
     - differentiate between cantrips (can cast each round), with spells that
    - examine items - use ability checks here
     - players need to have long descriptions
     - show health status
      - wandering...

    bugs:

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
from lib.magic import Magic
from lib.dungeon import Dungeon
from lib.dice import Dice
from lib.key import Key
from lib.door import Door

# import the MUD server class
from server.mud import Mud


class Game():
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self, mud):
        # start the server

        self._monster = Monster()

        self._room = Room()

        self._armor = Armor()

        self._weapon = Weapon()

        self._class = Classes()

        self._species = Species()

        self._monsterstats = MonsterStats()

        self._magic = Magic(mud)

        self._dungeon = Dungeon()

        self._dice = Dice()

        self._grid = self._dungeon.grid  # town

        self._proficiency = self._class.prof

        self._cr = self._monster.challenge

        self._classes = self._class.classes

        self._modifiers = self._class.mod

        self._species = self._species.species

        self._rooms = self._room.rooms

        self._mm = self._monster.mm

        self._monsterstats = self._monsterstats.monsterstats

        self._weapons = self._weapon.weapons

        self._armors = self._armor.armors

        self._magics = self._magic.magics

        self._mud = mud

        self._players = {}

        self._monsters = {}

        self._exits = ["north", "south", "east", "west"]

        self._tick = 6  # 6 seconds

        self._roll_dice = self._dice.roll

        self._key = Key()

        self._door = Door()

        # counter for assigning each client a new id
        self._nextid = 0

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

        return f"You are carrying a {', '.join(inventory[:-1])} and a {inventory[-1]}."

    def _format_coins(self, coins):
        """
        format coins
        """
        wallet = []

        plat, rem = self._rdiv(coins, 1000)
        if plat > 0:
            wallet.append(f"{int(plat)}p")

        gold, rem = self._rdiv(rem, 100)
        if gold > 0:
            wallet.append(f"{int(gold)}g")

        silv, rem = self._rdiv(rem, 10)
        if silv > 0:
            wallet.append(f"{int(silv)}s")

        copp, rem = self._rdiv(rem, 1)
        if copp > 0:
            wallet.append(f"{int(copp)}c")

        return " ".join(wallet)

    def _get_modifier(self, value):
        """get modifier"""
        for scores, modifer in self._modifiers.items():
            if value in scores:
                return modifer
        return value

    def _can_learn(self, uid, index):
        """get modifier"""
        player = self._players[uid]
        spell_classes = self._magics[index]["class"]

        if self._classes[player["class"]]["type"] not in spell_classes:
            return False

        if self._magic.levels[player["level"]][player["level"]] > 0:
            return True

        return False

    def _can_equip(self, uid, merch):
        """get modifier"""
        armor_types = self._classes[self._players[uid]["class"]]["armor"]
        weapon_types = self._classes[self._players[uid]["class"]]["weapon"]

        if "etype" not in merch.keys():
            return True

        if merch["etype"] not in ["one-hand", "two-hand", "armor"]:
            return True

        for weapon in self._weapons:
            if merch["type"] in weapon["type"]:
                if weapon["size"] in weapon_types:
                    return True
        for armor in self._armors:
            if merch["type"] in armor["type"]:
                if armor["size"] in armor_types:
                    return True
        return False

    def _get_stat(self, uid, stat):
        """calculate stat with species bonuses"""
        return self._classes[self._players[uid]["class"]][stat] \
            + self._species[self._players[uid]["species"]][stat]

    def _max_enc(self, uid):
        """determind max hp"""
        return self._players[uid]["strength"] * 15

    def _cur_enc(self, uid):
        """determind max hp"""
        cur_enc = 0
        for item in self._players[uid]["inventory"]:
            cur_enc += item["weight"]

        cur_enc += self._players[uid]["equipped"]["weapon"]["weight"]

        cur_enc += self._players[uid]["equipped"]["armor"]["weight"]

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
        if self._monsters[uid]["equipped"]["armor"]["size"] in ["light"]:
            return self._monsters[uid]["equipped"]["armor"]["ac"] + \
                self._get_modifier(self._monsters[uid]["dexterity"])
        if self._monsters[uid]["equipped"]["armor"]["size"] in ["medium"]:
            modifier = self._get_modifier(self._monsters[uid]["dexterity"])
            return self._monsters[uid]["equipped"]["armor"]["ac"] + \
                modifier if modifier < 3 else 2
        return self._monsters[uid]["equipped"]["armor"]["ac"]

    def _get_monster_weapon(self, uid):
        """determine ac"""
        weapon_of_choice = []
        wtype = self._monsters[uid]["weapon"]
        if not wtype:
            return self._weapons[0]

        for weapon in self._weapons:
            if wtype[0] in weapon["size"] \
                    and wtype[1] in weapon["etype"] \
                    and wtype[2] in weapon["modifier"]:
                weapon_of_choice.append(weapon)

        return random.choice(weapon_of_choice)

    def _get_monster_armor(self, uid):
        """determine ac"""
        armor_of_choice = []
        atype = self._monsters[uid]["armor"]

        if not atype:
            return self._armors[0]
        for armor in self._armors:
            if atype in armor["size"]:
                armor_of_choice.append(armor)
        return random.choice(armor_of_choice)

    def _monster_room(self, room):
        """ wheres that monster """

        return self._grid[room[0]][room[1]][room[2]]

    def _movement(self, coords):
        """
        return current room and possible exits
        """
        exits = []
        room = None

        z_coord = coords[0]
        x_coord = coords[1]
        y_coord = coords[2]

        room = self._grid[z_coord][x_coord][y_coord]
        print("current loc [{},{},{}] in {}.".format(
            z_coord, x_coord, y_coord, self._rooms[z_coord][room]["short"]))
        if self._grid[z_coord][x_coord - 1][y_coord] > 0:
            exits.append("north")
        if self._grid[z_coord][x_coord + 1][y_coord] > 0:
            exits.append("south")
        if self._grid[z_coord][x_coord][y_coord - 1] > 0:
            exits.append("west")
        if self._grid[z_coord][x_coord][y_coord + 1] > 0:
            exits.append("east")
        if self._grid[z_coord + 1][x_coord][y_coord] > 0:
            exits.append("down")
        if self._grid[z_coord - 1][x_coord][y_coord] > 0:
            exits.append("up")

        return room, exits

    def _get_hurt(self, mid):
        """ figure out how wounded a monster is """
        perc = (self._monsters[mid]["current_hp"]
                / float(self._monsters[mid]["max_hp"]) * 100)
        # healthy 85 - 100
        if 85 < perc < 101:
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

    def _process_drop_command(self, uid, params):
        """drop stuff"""

        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]

        for item in self._players[uid]["inventory"]:
            if params in item["type"]:
                if len(cur_room["floor"]) < 10:
                    cur_room["floor"].append(item)
                    self._players[uid]["inventory"].remove(item)
                    self._mud.send_message(
                        uid, f"You dropped your {item['type']}.")
                    return True
                self._mud.send_message(
                    uid, "You can't drop any more items here.")
                return False
        self._mud.send_message(
            uid, "Sorry, you don't seem to have that item.")
        return False

    def _process_get_command(self, uid, params):
        """get stuff"""

        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]

        for item in cur_room["floor"]:
            if params in item["type"]:
                self._players[uid]["inventory"].append(item)
                cur_room["floor"].remove(item)
                self._mud.send_message(
                    uid, f"You picked up a {item['type']}.")
                return True
        self._mud.send_message(
            uid, "Sorry, but no such item is here.")
        return False

    def _process_look_at_command(self, uid, params):
        """look at stuff"""

        _, valid_exits = self._movement(self._players[uid]["room"])

        # look at _rooms
        if params == "spellbook":
            spellbook = self._get_item_handle(
                "spellbook", self._players[uid]["inventory"])
            if spellbook:
                self._magic.look_at_spellbook(uid, spellbook)
            else:
                self._mud.send_message(
                    uid, "You don't seem to have a spellbook."
                )
            return

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
                    uid, "You can't see anything to the {}.".format(params))
            return True

        # look at monsters
        monsters_here = []
        for mid, monster in self._monsters.items():
            if monster["room"] == self._players[uid]["room"]:
                monsters_here.append(monster)
            for monster_here in monsters_here:
                if params in monster_here["name"]:
                    long = monster_here["long"]
                    if long.count('{}') > 1:
                        desc = long.format(
                            monster_here["equipped"]["armor"]["type"],
                            monster_here["equipped"]["weapon"]["type"]
                        )
                    elif long.count('{}') == 1:
                        desc = long.format(
                            monster_here["equipped"]["weapon"]["type"]
                        )
                    else:
                        desc = long
                    hurt = self._get_hurt(mid)
                    self._mud.send_message(
                        uid, (
                            desc + " The {} appears to be {}."
                            .format(monster["name"], hurt))
                        )
                else:
                    self._mud.send_message(
                        uid, "You don't see {} nearby.".format(params))
                return True

    def _process_long_look_command(self, uid):
        """
        write out the room and any players or items in it
        """
        has_light = []
        room, exits = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        cur_player = self._players[uid]

        for item in cur_player["inventory"]:
            if "effect" in item.keys():
                if item["effect"] == "light":
                    has_light.append(item)

        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["room"] == self._players[uid]["room"] and \
                    pid != uid:
                # ... and they have a name to be shown
                if player["name"] is not None:
                    # add their name to the list

                    for item in player["inventory"]:
                        if "effect" in item.keys():
                            if item["effect"] == "light":
                                has_light.append(item)

        if cur_room["dark"] and not has_light:
            self._mud.send_message(uid, "It's too dark to see.")
            return

        exit_list = ", ".join(exits)
        self._mud.send_message(uid, cur_room["long"] + exit_list)

    def _process_look_command(self, uid):
        """
        write out the room and any players or items in it
        """
        has_light = []
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        cur_player = self._players[uid]

        for item in cur_player["inventory"]:
            if "effect" in item.keys():
                if item["effect"] == "light":
                    has_light.append(item)

        players_here = []
        monsters_here = []
        items_here = []
        # go through every player in the game
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["room"] == self._players[uid]["room"] and \
                    pid != uid:
                # ... and they have a name to be shown
                if player["name"] is not None:
                    # add their name to the list
                    players_here.append(player["name"])

                    for item in player["inventory"]:
                        if "effect" in item.keys():
                            if item["effect"] == "light":
                                has_light.append(item)

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

        print(cur_room["dark"], has_light)
        if cur_room["dark"] and not has_light:
            self._mud.send_message(uid, "It's too dark to see.")
            return

        self._mud.send_message(uid, cur_room["short"])

        # TBD this logic is tortured.  fix it later
        if monsters_here:
            self._mud.send_message(uid, monster_line)
        if players_here and monsters_here or players_here \
                and not monsters_here:
            self._mud.send_message(uid, who)
        elif not players_here and not monsters_here:
            self._mud.send_message(uid, who)

        for item in cur_room["floor"]:
            items_here.append(item["type"])

        if items_here:
            if len(items_here) == 1:
                self._mud.send_message(
                    uid, f"There is a {items_here[0]} lying on the floor.")
            elif len(items_here) == 2:
                self._mud.send_message(
                    uid, (
                        f"There is a {items_here[0]} and a {items_here[1]} "
                        f"lying on the floor."
                    )
                )
            else:
                self._mud.send_message(
                    uid, (
                        f"There is a {', '.join(items_here[:-1])} and a "
                        f"{items_here[-1]} lying on the floor."
                    )
                )
        else:
            self._mud.send_message(uid, "There is nothing on the floor.")

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
        self._players[uid]["room"] = [1, 4, 2]
        self._players[uid]["fatigue"] = time.time()
        self._players[uid]["hit_dice"] = self._classes[command]["hit_dice"]
        self._players[uid]["level"] = 20
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
        self._players[uid]["xp"] = 1000000
        self._players[uid]["proficiency"] = (
            self._proficiency[self._players[uid]["level"]]
        )
        self._players[uid]["status"] = "Healthy"
        self._players[uid]["equipped"] = {
            "weapon": self._weapons[0],
            "armor": self._armors[0]
        }
        self._players[uid]["armor_class"] = self._armor_class(uid)
        self._players[uid]["inventory"] = []
        self._players[uid]["spellbook"] = []
        self._players[uid]["coins"] = (
            self._roll_dice(self._classes[command]["wealth"])
        )

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

    def _process_unknown_command(self, uid, command, params):
        """
        say stuff to other folks
        """
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["room"] == self._players[uid]["room"] \
                    and pid != uid:
                # send them a message telling them what the player said
                self._mud.send_message(
                    pid, (
                        "{} says: {}".format(
                            self._players[uid]["name"],
                            " ".join([command, params])
                        )
                    )
                )
                self._mud.send_message(uid, "--- Message Sent ---")

                return True

        self._mud.send_message(
            uid, "Sorry, that is not an appropriate command.")

        return False

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
        pclass = self._classes[player["class"]]

        if not params:
            self._mud.send_message(
                uid, "You need to specify what you want to equip.")
            return

        for item in player["inventory"]:
            if params in item["type"] and item["equip"]:
                if item["etype"] == "armor":
                    if not item["size"] in pclass["armor"]:
                        self._mud.send_message(
                            uid, "Sorry, you may not equip that.")
                        return
                    if player["equipped"]["armor"]:
                        self._process_unequip_command(
                            uid, player["equipped"]["armor"]["type"])
                    player["equipped"]["armor"] = item
                    player["armor_class"] = self._armor_class(uid)
                    player["inventory"].remove(item)
                    self._mud.send_message(uid, f"You equipped {item['type']}.")

                elif item["etype"] in ["one-hand", "two-hand"]:
                    if not item["size"] in pclass["weapon"]:
                        self._mud.send_message(
                            uid, "Sorry, you may not equip that.")
                        return
                    if player["equipped"]["weapon"]:
                        self._process_unequip_command(
                            uid, player["equipped"]["weapon"]["type"])
                    player["equipped"]["weapon"] = item
                    player["inventory"].remove(item)
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
        if len(list(self._monsters.keys())) < 9:
            self._spawn_monsters(room=[1, 4, 3])
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
            self._players[uid]["current_hp"] += self._roll_dice([1, 4])
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
        self._mud.send_message(uid, "Proficiency:  {}".format(
            self._players[uid]["proficiency"]))
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
        """ move around """
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
        cur_room_num, cur_exits = self._movement(self._players[uid]["room"])

        cur_room = self._rooms[self._players[uid]["room"][0]][cur_room_num]
        cur_player = self._players[uid]
        cur_player_room = self._players[uid]["room"]
        next_player_room = cur_player_room.copy()

        # if the specified exit is found in the room's exits list
        if door in cur_exits:
            print("_process_go_command:cur_room", cur_room)
            print("next_player_room", next_player_room)
            # update the player's current room to the one the exit leads to
            if door == "south":
                next_player_room[1] += 1
            if door == "north":
                next_player_room[1] -= 1
            if door == "east":
                next_player_room[2] += 1
            if door == "west":
                next_player_room[2] -= 1
            if door == "up":
                next_player_room[0] -= 1
            if door == "down":
                next_player_room[0] += 1

            next_room_num, _ = (
                self._movement(next_player_room)
            )
            next_room = self._rooms[next_player_room[0]][next_room_num]
            print("next_player_room", next_player_room)
            print("next_room_num", next_room_num)
            print("next_room", next_room)

            # TBD only check for doors and traps on *next room* not cur_room

            if 'door' in next_room.keys():
                keychain = self._get_item_handle("key", cur_player["inventory"])
                print("keychain", keychain)
                key_num = next_room["door"]
                key = self._key.keys[key_num]
                door = self._door.doors[key_num]
                print("key", key)
                print("door", door)
                if keychain:
                    if key["type"] == keychain["type"]:
                        self._mud.send_message(
                            uid,
                            f"Your {key['type']} unlocks the {door['type']}."
                        )
                    else:
                        self._mud.send_message(
                            uid, f"The {door['type']} blocks your passage.")
                        return
                else:
                    self._mud.send_message(
                        uid, f"The {door['type']} blocks your passage.")
                    return

            # move player to next room
            self._players[uid]["room"] = next_player_room

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
        self._process_attack(uid, params)

    def _get_loot(self, player, loots):
        """
        try to kill some stuff why not
        """
        loot = []

        for loot_type in loots:
            if 'keys' in loot_type:
                for num in loot_type['keys']:
                    loot.append(self._key.keys[num])

        player["inventory"] += loot

    def _process_attack(self, uid, target, spell=None):
        """
        try to kill some stuff why not
        """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        monsters = self._monsters.copy()
        monsters_here = {}
        for hmid, hmonster in monsters.items():
            if target in hmonster["name"] and hmonster["room"] \
                    == self._players[uid]["room"]:
                monsters_here.update({hmid: hmonster})

        if monsters_here:
            mid, monster = random.choice(list(monsters_here.items()))
            if time.time() - self._players[uid]["fatigue"] > self._tick:
                damage = 0
                if spell is not None:
                    damage = self._process_spell_damage(
                        uid, spell, monster)
                else:
                    damage = self._process_melee_damage(
                        uid, monster)

                if damage is not None:
                    monster["current_hp"] -= damage

                if monster["current_hp"] < 1:
                    self._mud.send_message(
                        uid,
                        (
                            "The {} falls to the ground "
                            "lifeless!".format(monster["name"])
                        )
                    )

                    # set the clock to respawn monsters if this is a lair
                    if "spawn_timer" in cur_room.keys():
                        cur_room["spawn_timer"] = time.time()

                    # check for loot
                    if "loot" in cur_room.keys():
                        print(cur_room["loot"])
                        self._get_loot(self._players[uid], cur_room['loot'])
                        print(self._players[uid])

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

                    if monster["equipped"]["weapon"]:
                        if len(cur_room["floor"]) < 10:
                            cur_room["floor"].append(
                                monster["equipped"]["weapon"]
                            )
                            self._mud.send_message(
                                uid, (
                                    f"The {monster['name']} dropped a "
                                    f"{monster['equipped']['weapon']['type']} "
                                    f"on the floor."
                                )
                            )
                    if monster["equipped"]["armor"]:
                        if len(cur_room["floor"]) < 10:
                            cur_room["floor"].append(
                                monster["equipped"]["armor"]
                            )
                            self._mud.send_message(
                                uid, (
                                    f"The {monster['name']} dropped a "
                                    f"{monster['equipped']['armor']['type']} "
                                    f"on the floor."
                                )
                            )
                    del self._monsters[mid]
            else:
                self._mud.send_message(
                    uid, (
                        "You are still physically exhausted from your "
                        "previous activities!"
                    )
                )
        else:
            self._mud.send_message(
                uid, f"Sorry, you don't see {target} nearby.")

    def _process_spell_damage(self, uid, spell, target):
        """ try to cast a damaging spell """
        player = self._players[uid]

        xp_incr = int(self._cr[target["cr"]] / target["max_hp"])
        damage = self._roll_dice(spell["effect"])

        player["fatigue"] = time.time()
        player["xp"] += xp_incr * damage
        self._mud.send_message(
            uid, spell["description"].format(target["name"], damage))

        return damage

    def _process_melee_damage(self, uid, target):
        """
        try to kill some stuff why not
        """
        player = self._players[uid]

        attack = (
            self._roll_dice([1, 20])
            + self._get_modifier(player["strength"])
            + player["proficiency"]
        )

        xp_incr = int(self._cr[target["cr"]] / target["max_hp"])

        if attack > target["armor_class"]:
            dice = (
                self._roll_dice(
                    player["equipped"]["weapon"]["damage"]
                )
            )

            damage = dice + self._get_modifier(player["strength"])

            player["fatigue"] = time.time()
            player["xp"] += xp_incr * damage

            self._mud.send_message(
                uid,
                "Your attack hits {} for {} damage.".format(
                    target["name"], damage))

            return damage
        else:
            self._mud.send_message(
                uid, (
                    "Your poorly executed attacked misses "
                    "the {}.".format(target["name"])
                )
            )
            self._players[uid]["fatigue"] = time.time()

    def _process_spell_heal(self, uid, spell, target):
        """
        try to kill some stuff why not
        """

    def _process_spell_enchant(self, uid, spell, target):
        """
        try to kill some stuff why not
        """

    def _process_spell_buff(self, uid, spell, target):
        """
        try to kill some stuff why not
        """

    def _process_cast_command(self, uid, params):
        """
        try to kill some stuff why not
        """
        player = self._players[uid]

        spell = None
        target = None

        if len(params.split()) > 1:
            spell, target = params.split()
        else:
            spell = params

        spellbook = self._get_item_handle("spellbook", player["inventory"])

        if spellbook is not None:
            print(spellbook)
            spell = self._get_spell_handle(spell, spellbook["spells"])

#     def _process_attack(self, uid, target, attack_type="melee", spell=None):

        if spell is not None:
            if spell["result"] == "damage":
                if target is not None:
                    self._process_attack(uid, target, spell)

            elif spell["result"] == "buff":
                if target is not None:
                    self._process_spell_buff(uid, spell, target)
                else:
                    self._process_spell_buff(uid, spell, player)
            elif spell["resutl"] == "enchant":
                if target is not None:
                    self._process_spell_enchant(uid, spell, target)
                else:
                    self._process_spell_enchant(uid, spell, player)
            elif spell["result"] == "heal":
                if target is not None:
                    self._process_spell_heal(uid, spell, target)
                else:
                    self._process_spell_heal(uid, spell, player)
        else:
            self._mud.send_message(
                uid, f"Sorry, you don't seem to have learned {params.split()[0]}")

    def _spawn_monsters(self, mob=None, room=None):
        """
        check lairs and spawn monsters if they are empty
        """
        print(self._nextid, room, mob)
        print([monster["room"] for num, monster in self._monsters.items()])
        if not mob:
            self._monsters[self._nextid] = (
                random.choice([x for x in self._mm if x["cr"] < 2]).copy()
            )
        else:
            self._monsters[self._nextid] = self._mm[mob].copy()

        self._monsters[self._nextid]["room"] = room
        self._monsters[self._nextid]["proficiency"] = (
            self._proficiency[self._monsters[self._nextid]["cr"]]
        )
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
            "weapon": self._get_monster_weapon(self._nextid),
            "armor": self._get_monster_armor(self._nextid)
        }
        self._monsters[self._nextid]["armor_class"] = (
            self._monster_armor_class(self._nextid)
        )
        self._monsters[self._nextid]["regen_hp"] = time.time()
        self._monsters[self._nextid]["armor_class"] = (
            self._monster_armor_class(self._nextid))
        self._monsters[self._nextid]["coins"] = self._roll_dice(
            self._monsterstats[self._monsters[self._nextid]["cr"]]["wealth"])
        print(
            "spawned {} with cr {} that has {} xp in {}.".format(
                self._monsters[self._nextid]["name"],
                self._monsters[self._nextid]["cr"],
                self._cr[self._monsters[self._nextid]["cr"]],
                room
            )
        )
        print([monster["room"] for num, monster in self._monsters.items()])
        print()

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
        try:
            monster = self._monsters[mid]
        except KeyError as error:
            print("monster gone ", error)
            return False

        room = self._monster_room(monster["room"])
        cur_room = self._rooms[monster["room"][0]][room]
        players_here = {}
        monsters_here = {}

        for pid, player in self._players.items():
            if player["room"] == monster["room"]:
                players_here.update({pid: player})

        for tid, target in self._monsters.items():
            if target["room"] == monster["room"] and tid != mid:
                monsters_here.update({tid: target})

        if players_here:
            pid, player = random.choice(list(players_here.items()))

            if time.time() - monster["fatigue"] > self._tick:

                attack = (
                    self._roll_dice([1, 20])
                    + self._get_modifier(monster["strength"])
                    + monster["proficiency"]
                )
                print("{} attack: {}".format(monster["name"], attack))
                print("{} ac: {}".format(player["name"], player["armor_class"]))
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
                    for uid, _ in self._players.items():
                        if uid != pid:
                            self._mud.send_message(
                                uid, (
                                    "The {} attacked {} with their {}!".format(
                                        monster["name"],
                                        player["name"],
                                        monster["equipped"]["weapon"]["type"]
                                    )
                                )
                            )
                    player["current_hp"] -= damage
                    if player["current_hp"] < 1:
                        self._mud.send_message(pid, (
                            "As the final blow strikes your body you "
                            "fall unconscious."))
                        self._mud.send_message(pid, (
                            "You awaken after an unknown amount of "
                            "time..."))
                        self._players[pid]["room"] = [1, 4, 2]
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
        else:
            if not monsters_here:
                return False

            pid, player = random.choice(list(monsters_here.items()))
            if player["name"].split(" ")[-1] == monster["name"].split(" ")[-1]:
                return False

            if time.time() - monster["fatigue"] > self._tick:

                attack = (
                    self._roll_dice([1, 20])
                    + self._get_modifier(monster["strength"])
                    + monster["proficiency"]
                )
                print("{} attack: {}".format(monster["name"], attack))
                print("{} ac: {}".format(player["name"], player["armor_class"]))
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
                    print(
                        "{} attacked {} for {} damage".format(
                            monster["name"], player["name"], damage))
                    player["current_hp"] -= damage
                    if player["current_hp"] < 1:
                        print(
                            "{} killed {}.".format(
                                monster["name"], player["name"]))
                        self._monsters[mid]["coins"] += player["coins"]

                        if player["equipped"]["weapon"]:
                            if len(cur_room["floor"]) < 10:
                                cur_room["floor"].append(
                                    player["equipped"]["weapon"]
                                )
                                print(
                                        f"The {player['name']} dropped a "
                                        f"{player['equipped']['weapon']['type']} "
                                        f"on the floor."
                                    )
                        if player["equipped"]["armor"]:
                            if len(cur_room["floor"]) < 10:
                                cur_room["floor"].append(
                                    player["equipped"]["armor"]
                                )
                                print(
                                        f"The {player['name']} dropped a "
                                        f"{player['equipped']['armor']['type']} "
                                        f"on the floor."
                                    )

                        del self._monsters[pid]
                    monster["fatigue"] = time.time()
                else:
                    monster["fatigue"] = time.time()

    def _process_list_command(self, uid):
        """ list items if that room has them """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]

        if "items" in cur_room.keys():
            self._mud.send_message(uid, "")
            self._mud.send_message(uid, "+======================+========+")
            self._mud.send_message(uid, "| Item                 | Price  |")
            self._mud.send_message(uid, "+----------------------+--------+")
            try:
                light = [
                    x for x in cur_room["items"]
                    if x["size"] == "light"
                ]
                medium = [
                    x for x in cur_room["items"]
                    if x["size"] == "medium"
                ]
                heavy = [
                    x for x in cur_room["items"]
                    if x["size"] == "heavy"
                ]
                for item in sorted(light, key=lambda x: x['value']):
                    self._mud.send_message(
                        uid, (
                            f"| {item['type']:21}"
                            f"| {self._format_coins(item['value']):7}|"
                        )
                    )
                self._mud.send_message(uid, "+----------------------+--------+")
                for item in sorted(medium, key=lambda x: x['value']):
                    self._mud.send_message(
                        uid, (
                            f"| {item['type']:21}"
                            f"| {self._format_coins(item['value']):7}|"
                        )
                    )
                self._mud.send_message(uid, "+----------------------+--------+")
                for item in sorted(heavy, key=lambda x: x['value']):
                    self._mud.send_message(
                        uid, (
                            f"| {item['type']:21}"
                            f"| {self._format_coins(item['value']):7}|"
                        )
                    )
            except KeyError:
                for item in sorted(
                        cur_room["items"],
                        key=lambda x: x['value']
                        ):
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

    def _process_list_at_command(self, uid, params):
        """ list items if that room has them """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]

        if not self._classes[self._players[uid]["class"]]["magic"]:
            self._mud.send_message(uid, "Sorry, your class cannot use magic.")
            return False

        if "spells" in cur_room.keys():

            self._mud.send_message(uid, "")
            self._mud.send_message(uid, "+======================+========+")
            self._mud.send_message(uid, "| Spell                | Price  |")
            self._mud.send_message(uid, "+----------------------+--------+")

            for item in sorted(
                    cur_room["spells"],
                    key=lambda x: x['value']
                    ):
                if self._classes[self._players[uid]["class"]]["type"] \
                        in item["class"]:
                    self._mud.send_message(
                        uid, (
                            f"| {item['name']:21}"
                            f"| {self._format_coins(item['value']):7}|"
                        )
                    )
            self._mud.send_message(uid, "+======================+========+")

        else:
            self._mud.send_message(
                uid, "Sorry, that is not an appropriate command.")

    def _process_sell_command(self, uid, params):
        """ list items if that room has them """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        merch = None
        merchant_wants = False

        if "items" not in cur_room.keys():
            self._mud.send_message(uid, "Sorry, you can't do that here.")
            return False

        for inv in self._players[uid]["inventory"]:
            if params in inv["type"]:
                merch = inv
                break

        if merch is None:
            self._mud.send_message(uid, "Sorry, you don't seem to have that.")
            return False

        for item in cur_room["items"]:
            if merch["etype"] in item["etype"]:
                merchant_wants = True
                break

        if merchant_wants:
            self._mud.send_message(
                uid, (
                    f"You just sold {merch['type']} for "
                    f"{self._format_coins(merch['value'])}."
                )
            )
            self._players[uid]["coins"] += merch['value']
            self._players[uid]["inventory"].remove(merch)
        else:
            self._mud.send_message(
                uid, f"The merchant doesn't want {merch['type']}.")

    @staticmethod
    def _get_item_handle(name, items):
        """ return item handle """

        item = None
        for item in items:
            if name in item["type"]:
                return item

        return None

    @staticmethod
    def _get_spell_handle(name, spells):
        """ return item handle """

        spell = None
        for spell in spells:
            if name in spell["name"]:
                return spell

        return None

    def _process_learn_command(self, uid, params):
        """ list items if that room has them """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        spell = None
        index = 0

        if "spells" in cur_room.keys():
            for index, spell in enumerate(cur_room["spells"]):
                if params in spell["name"]:
                    break

            if spell:
                if not self._can_learn(uid, index):
                    self._mud.send_message(
                        uid, (
                            "Sorry, you may not learn {}.".format(spell["name"])
                        )
                    )
                    return False

                if "spellbook" not in \
                        [x["type"] for x in self._players[uid]["inventory"]]:
                    self._mud.send_message(
                        uid, (
                            "Sorry, you don't have a spellbook."
                        )
                    )
                    return False

                if self._players[uid]["coins"] > spell["value"]:
                    spellbook = self._get_item_handle(
                        "spellbook", self._players[uid]["inventory"])
                    spellbook["spells"].append(spell)
                    self._players[uid]["coins"] -= spell["value"]
                    self._mud.send_message(
                        uid, (
                            f"You just learned {spell['name']} for "
                            f"{self._format_coins(spell['value'])}."
                        )
                    )
                else:
                    self._mud.send_message(
                        uid, f"You can't afford to learn {spell['name']}.")
            else:
                self._mud.send_message(
                    uid, f"This shop doesn't offer {params}.")
        return False

    def _process_train_command(self, uid):
        """ list items if that room has them """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        player = self._players[uid]
        merch = None

        if "items" in cur_room.keys():
            for item in cur_room["items"]:
                if "training" in item["type"]:
                    merch = item
                    break

        if not merch:
            self._mud.send_message(
                uid, "Sir, you can't train here, this is a Wendy's.")
            return

        amount = player["level"] * player["level"] * merch["value"]
        if self._class.check_level(player):
            if player["coins"] > amount:
                self._class.level_up(player)
                player["coins"] -= amount
                self._mud.send_message(
                    uid, (
                        f"You just purchased {merch['type']} for "
                        f"{self._format_coins(amount)}."
                    )
                )
            else:
                self._mud.send_message(
                    uid, f"You can't afford {merch['type']}.")
        else:
            self._mud.send_message(
                uid, "You are not ready for training, yet.")

    def _process_buy_command(self, uid, params):
        """ list items if that room has them """
        room, _ = self._movement(self._players[uid]["room"])
        cur_room = self._rooms[self._players[uid]["room"][0]][room]
        merch = None

        if "items" in cur_room.keys():
            for item in cur_room["items"]:
                if params in item["type"]:
                    merch = item
                    break

            if merch:
                if not self._can_equip(uid, merch):
                    self._mud.send_message(
                        uid, (
                            "Sorry, you may not equip {}.".format(merch["type"])
                        )
                    )
                    return False
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

                self._players[uid]["name"] = command.capitalize()

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
            elif command in ["look", "l"]:

                # look around to see who and what is around
                if params == "":
                    self._process_long_look_command(uid)
                else:
                    self._process_look_at_command(uid, params)

            # 'look' command
            elif command in [""]:

                # look around to see who and what is around
                self._process_look_command(uid)

            # 'go' command
            elif command in ["go", "east", "west", "north", "south", "up", "down"]:

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
                if params:
                    self._process_list_at_command(uid, params)
                else:
                    self._process_list_command(uid)

            # 'list' command
            elif command == "buy":

                # go to another rooms
                if "training" in params:
                    self._process_train_command(uid)
                else:
                    self._process_buy_command(uid, params)

            # 'list' command
            elif command == "sell":

                # go to another rooms
                self._process_sell_command(uid, params)

            elif command == "inv":

                # go to another rooms
                self._process_inv_command(uid)

            elif command == "equip":

                # go to another rooms
                self._process_equip_command(uid, params)

            elif command == "drop":

                # go to another rooms
                self._process_drop_command(uid, params)

            elif command == "get":

                # go to another rooms
                self._process_get_command(uid, params)

            elif command == "learn":

                # go to another rooms
                self._process_learn_command(uid, params)

            elif command == "cast":

                # go to another rooms
                self._process_cast_command(uid, params)

            # 'exit' command
            elif command == "quit":

                # go to another rooms
                self._process_quit_command(uid)

            # some other, unrecognised command
            else:
                # send back an 'unknown command' message

                self._process_unknown_command(uid, command, params)

    def _monsters_here(self, room):
        monsters_here = []
        for _, monster in self._monsters.items():
            if monster["room"] == room:
                monsters_here.append(monster)

        return bool(monsters_here)

    def _populate_lairs(self):
        """ check for all rooms that are lairs and populate them """
        lairs = {}

        for z_coord, level in enumerate(self._grid):
            for y_coord, row in enumerate(level):
                for x_coord, room_num in enumerate(row):
                    if "lair" in self._rooms[z_coord][room_num]:
                        lair = self._rooms[z_coord][room_num]
                        room = (z_coord, y_coord, x_coord)
                        lairs.update({room: lair})

        if not lairs:
            return

        for lroom, llair in lairs.items():

            if self._monsters_here(list(lroom)):
                continue

            for _ in range(llair["num"]):
                if time.time() - llair["spawn_timer"] \
                        > self._tick * 10:
                    self._spawn_monsters(
                        random.choice(llair["mobs"]), list(lroom))

    def check_for_monsters(self):
        """
        spawn monsters and move them around
        """

        # only try to populate lairs every 6s or so
        if time.time() - self._monster.populate > self._tick:

            # populate lairs
            self._populate_lairs()

            # reset populate timer
            self._monster.populate = time.time()

        monsters = self._monsters.copy()

        for mid, _ in monsters.items():

            # monsters attack first and ask questions later
            self._monsters_attack(mid)

            # monsters wander if no one is around and run if they are injured
            self._monsters_move()

    def check_for_status(self):
        """
        spawn monsters and move them around
        """

        for pid, player in self._players.items():

            if player["name"] is None:
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
