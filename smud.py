#!/usr/bin/env python

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

author: Mark Frimston - mfrimston@gmail.com
"""

import random
import sys
import time

# import the MUD server class
from mud import Mud


class Game():
    """
    This class contains all of the functions to allow the game to operate
    """

    _monsters = {}

    _mud = None

    _players = {}

    _commands = []

    _grid = []

    _rooms = []

    def __init__(self, mud):
        # start the server

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

        self._rooms = [
            {  # 0
                "short": "You can't be here.",
                "long": "Go away."
            },
            {  # 1
                "short": "You're on the docks.",
                "long": "You're in the north plaza. It's nice."
            },
            {  # 2
                "short": "You're in the guild hall.",
                "long": "You're in the south plaza. It's nice."
            },
            {  # 3
                "short": "You're in the north plaza.",
                "long": "You're in the arena. It sucks."
            },
            {  # 4
                "short": "You're in the south plaza.",
                "long": "You're in the general store. Stuff."
            },
            {  # 5
                "short": "You're in the magic shop.",
                "long": "You're in the general store. Stuff."
            },
            {  # 6
                "short": "You're in the armor shop.",
                "long": "You're in the general store. Stuff."
            },
            {  # 7
                "short": "You're in the weapons shop.",
                "long": "You're in the general store. Stuff."
            },
            {  # 8
                "short": "You're in the arena.",
                "long": "You're in the general store. Stuff."
            },
            {  # 9
                "short": "You're in the temple.",
                "long": "You're in the general store. Stuff."
            },
            {  # 10
                "short": "You're in the general store.",
                "long": "You're in the general store. Stuff."
            },
            {  # 11
                "short": "You're in the tavern.",
                "long": "You're in the general store. Stuff."
            },
            {  # 11
                "short": "You're on a path.",
                "long": "You're in the general store. Stuff."
            }
        ]

        self._mm = [
            {  # 0
                "name": "cave bear",
                "long": "The cave bear has dark brown fur and stands well over \
                         seven feet tall at the shoulder. Its teeth and claws \
                         gleam like daggers as it sizes you up.",
                "room": [4, 3]
            },
            {  # 1
                "name": "huge rat",
                "long": "The huge rat resembles rats you've seen before, \
                         except that it is about two feet tall at the \
                         shoulder, and seems much more aggressive.",
                "room": [1, 1]
            },
            {  # 2
                "name": "imp",
                "long": "The imp is a tiny humanoid with pointed ears and \
                         bright red skin. It stands just over two feet in \
                         height and is armed with a dagger.",
                "room": [1, 1]
            },
            {
                "name": "female kobold",
                "long": "The kobold is a small humanoid with doglike facial \
                         features and is covered with coarse body hair. She \
                         stands just over three feet in height, is wearing a \
                         filthy tunic, and is armed with {small one-handed}.",
                "room": [1, 1]
            },
            {
                "name": "kobold",
                "long": "The kobold is a small humanoid with doglike facial \
                         features and is covered with coarse body hair. He \
                         stands just under four feet in height, is wearing a \
                         filthy tunic, and is armed with {small one-handed}.",
                "room": [1, 1]
            },
            {
                "name": "female orc",
                "long": "The orc is a smallish humanoid with piglike facial \
                         features and is covered sparsely by coarse body hair. \
                         She stands just over four feet in height, is wearing \
                         a leather tunic, and is armed with club.",
                "room": [1, 1]
            },
            {
                "name": "orc",
                "long": "The orc is a smallish humanoid with piglike facial \
                         features and is covered sparsely by coarse body hair. \
                         He stands just under five feet in height, is wearing \
                         a leather cuirass, and is armed with club.",
                "room": [1, 1]
            },
            {
                "name": "skeleton warrior",
                "long": "The skeleton warrior is wearing tattered armor and \
                         mouldering bits of old clothing, and is armed with \
                         {large two-handed} {1}.",
                "room": [1, 1]
            },
            {
                "name": "giant bat",
                "long": "The giant bat has a wingspan of over twelve feet and \
                         has wicked looking claws and teeth.",
                "room": [1, 1]
            },
            {
                "name": "lizard woman",
                "long": "The lizard woman is a five foot tall bipedal \
                         humanoid who's features resemble those of a large \
                         lizard. She has greyish scaley skin, and sharp claws \
                         and teeth. The lizard woman is armed with scimitar.",
                "room": [1, 1]
            },
            {
                "name": "lizard man",
                "long": "The lizard man is a six foot tall bipedal humanoid \
                         who's features resemble those of a large lizard. He \
                         has greenish scaley skin, and sharp claws and teeth. \
                         The lizard man is armed with scimitar.",
                "room": [1, 1]
            },
            {
                "name": "female hobgoblin",
                "long": "The hobgoblin is a squat apelike humanoid with dark \
                         skin and pointed ears. She stands just under five \
                         feet tall, is wearing a leather cuirass, and is armed \
                         with small one-handed.",
                "room": [1, 1]
            },
            {
                "name": "hobgoblin",
                "long": "The hobgoblin is a squat apelike humanoid with dark \
                         skin and pointed ears. He stands just over five feet \
                         tall, is wearing a leather cuirass, and is armed \
                         with {small one-handed} {1}.",
                "room": [1, 1]
            },
            {
                "name": "cave bear",
                "long": "The cave bear has dark brown fur and stands well \
                         over seven feet tall at the shoulder. Its teeth and \
                         claws gleam like daggers as it sizes you up.",
                "room": [1, 1]
            },
            {
                "name": "female cyclops",
                "long": "The cyclops resembles a very large woman with only \
                         one eye in the center of her forehead. She stands \
                         over eleven feet tall, and is armed with a spiked \
                         club.",
                "room": [1, 1]
            },
            {
                "name": "cyclops",
                "long": "The cyclops resembles a very large man with only one \
                         eye in the center of his forehead. He stands over \
                         twelve feet tall, and is armed with a spiked club.",
                "room": [1, 1]
            },
            {
                "name": "female minotaur",
                "long": "The minotaur has the upper torso of a muscular woman,\
                         and the head, legs, and hooves of a bull. She is \
                         wearing ringmail armor, and is armed with large \
                         one-handed.",
                "room": [1, 1]
            },
            {
                "name": "minotaur",
                "long": "The minotaur has the upper torso of a muscular man, \
                         and the head, legs, and hooves of a bull. He is \
                         wearing ringmail armor, and is armed with large \
                         one-handed.",
                "room": [1, 1]
            },
            {
                "name": "ogress",
                "long": "The ogress resembles an enormous and very ugly woman. \
                         She stands over seven feet tall and is very muscular. \
                         Her clothing is filthy and poorly made. She is armed \
                         with {large two-handed} {1}.",
                "room": [1, 1]
            },
            {
                "name": "ogre",
                "long": "The ogre resembles an enormous and very ugly man. \
                         He stands over eight feet tall and is very muscular. \
                         His clothing is filthy and poorly made. He is armed \
                         with {0} {1}.",
                "room": [1, 1]
            }
        ]

        self._mud = mud

        self._players = {}

        self._monsters = {}

        self._commands = [
            "look", "north", "south", "east", "west", "help", "say"
        ]

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
        self._players[uid]["name"] = command
        self._players[uid]["room"] = [4, 2]
        self._players[uid]["fatigue"] = time.time()
        self._players[uid]["hit_points"] = 13
        self._players[uid]["armor_class"] = 18
        self._players[uid]["strength"] = 17
        self._players[uid]["dexterity"] = 10
        self._players[uid]["constitution"] = 16
        self._players[uid]["intelligence"] = 8
        self._players[uid]["wisdon"] = 13
        self._players[uid]["charisms"] = 12
        print(self._players)

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

    def _process_go_command(self, uid, params):
        """
        move around
        """

        # get the exit and store it
        door = params.lower()

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
        for mid, monster in self._monsters.items():
            if params in monster["name"] and monster["room"] \
                    == self._players[uid]["room"]:
                if time.time() - self._players[uid]["fatigue"] > 15:
                    self._mud.send_message(
                        uid, "You attack {}.".format(monster["name"]))
                    del self._monsters[mid]
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
        if not self._monsters:
            self._monsters[0] = random.choice(self._mm)
            self._monsters[0]["room"] = [4, 3]
            self._monsters[0]["fatigue"] = time.time()
            self._monsters[0]["hit_points"] = 13
            self._monsters[0]["armor_class"] = 18
            self._monsters[0]["strength"] = 17
            self._monsters[0]["dexterity"] = 10
            self._monsters[0]["constitution"] = 16
            self._monsters[0]["intelligence"] = 8
            self._monsters[0]["wisdon"] = 13
            self._monsters[0]["charisms"] = 12
            print("spawned {}".format(self._monsters[0]["name"]))

    def _monsters_move(self):
        """
        if monsters aren't tethered to a lair, move them around
        """

    def _monsters_attack(self, mid):
        """
        monsters always attack if they are able.  beware.
        """
        for pid, player in self._players.items():
            if player["room"] == self._monsters[mid]["room"]:
                if time.time() - self._monsters[mid]["fatigue"] > 15:
                    self._mud.send_message(
                        pid, (
                            "The {} attacked you with their shortsword for 4 "
                            "damage!".format(self._monsters[mid]["name"])))
                    self._monsters[mid]["fatigue"] = time.time()

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
                "room": None,
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

                self._process_new_player(uid, command)

            # 'help' command
            elif command == "help":

                # send the player back the list of possible commands
                self._process_help_command(uid)

            # 'say' command
            elif command == "say":

                # go through every player in the game
                self._process_say_command(uid, params)

            # 'look' command
            elif command == "look":

                # look around to see who and what is around
                self._process_look_command(uid)

            # 'go' command
            elif command == "go":

                # go to another rooms
                self._process_go_command(uid, params)

            # "attack" command
            elif command in ["attack", "a"]:

                # let's gooooo
                self._process_attack_command(uid, params)

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
        self._spawn_monsters()

        for mid, _ in self._monsters.items():

            # monsters attack first and ask questions later
            self._monsters_attack(mid)

            # monsters wander if no one is around and run if they are injured
            self._monsters_move()


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

    return 0


if __name__ == '__main__':
    sys.exit(main())
