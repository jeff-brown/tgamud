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

        self._monsters = {}

        self._mud = mud

        self._players = {}

        self._commands = [
            "look", "north", "south", "east", "west", "help", "say"
        ]

    def _movement(self, uid):
        """
        return current room and possible exits
        """
        exits = []
        room = None

        x_coord = self._players[uid]["grid"][0]
        y_coord = self._players[uid]["grid"][1]

        room = self._grid[x_coord][y_coord]
        print("{} coords: ({}, {})".format(self._players[uid]["name"], x_coord, y_coord))
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
        # go through every player in the game
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["grid"] == self._players[uid]["grid"] and \
                    pid != uid:
                # ... and they have a name to be shown
                if player["name"] is not None:
                    # add their name to the list
                    players_here.append(player["name"])

        # send player a message containing the list of players in the room
        if players_here:
            who = "{} are here with you.".format(", ".join(players_here))
        else:
            who = "There is nobody here."

        self._mud.send_message(uid, self._rooms[room]["short"])
        self._mud.send_message(uid, who)
        self._mud.send_message(uid, "You can go {}.".format(", ".join(exits)))

    def _write_help(self, uid):
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

    def _process_new_player(self, uid, command):
        """
        add a new players name to the dictionary and stick them in a room
        """
        self._players[uid]["name"] = command
        self._players[uid]["grid"] = [4, 2]

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
            if player["grid"] == self._players[uid]["grid"] \
                    and pid != uid:
                # send them a message telling them what the player said
                self._mud.send_message(pid, "{} says: {}".format(
                    self._players[uid]["name"], params))

    def _process_exit_command(self, uid):
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
                if player["grid"] == self._players[uid]["grid"] \
                        and pid != uid:
                    # send them a message telling them that the player
                    # left the room
                    self._mud.send_message(
                        pid, "{} just left to the {}.".format(
                            self._players[uid]["name"], door))

            # update the player's current room to the one the exit leads to
            if door == "south":
                self._players[uid]["grid"][0] += 1
            if door == "north":
                self._players[uid]["grid"][0] -= 1
            if door == "east":
                self._players[uid]["grid"][1] += 1
            if door == "west":
                self._players[uid]["grid"][1] -= 1

            # go through all the players in the game
            for pid, player in self._players.items():
                # if player is in the same (new) room and isn't the player
                # sending the command
                if player["grid"] == self._players[uid]["grid"] \
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

    def check_for_new_players(self):
        """
        check to see if any new connections arrived since last update
        """
        # go through any newly connected players
        for pid in self._mud.get_new_players():

            # add the new player to the dictionary, noting that they've not been
            # named yet.
            # The dictionary key is the player's id number. We set their room to
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

            # if for any reason the player isn't in the player map, skip them and
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

            # if for any reason the player isn't in the player map, skip them and
            # move on to the next one
            if uid not in self._players:
                continue

            # if the player hasn't given their name yet, use this first command as
            # their name and move them to the starting room.
            if self._players[uid]["name"] is None:

                self._process_new_player(uid, command)

            # 'help' command
            elif command == "help":

                # send the player back the list of possible commands
                self._write_help(uid)

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

            # 'exit' command
            elif command == "exit":

                # go to another rooms
                self._process_exit_command(uid)

            # some other, unrecognised command
            else:
                # send back an 'unknown command' message
                self._mud.send_message(
                    uid, "Unknown command '{}'".format(command))


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

        game.check_for_new_players()

        game.check_for_disconnected_players()

        game.check_for_new_commands()

    return 0


if __name__ == '__main__':
    sys.exit(main())
