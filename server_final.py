# General layout modified from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
import socket
import threading
import sys
import random

# Server class which handles users connecting
class Server():
    def __init__(self, addresses):
        self.addresses = addresses

    def connecting(self):
        while True:
            client_socket, client_socket_address = server_socket.accept()
            print(f"{client_socket_address[0]}:{client_socket_address[1]} has connected.")

            welcome = "Welcome to Whist!"
            welcome = welcome.encode('utf-8')
            buff = f"{len(welcome):<{head}}".encode('utf-8')
            client_socket.send(buff + welcome)

            self.addresses[client_socket] = client_socket_address
            threading.Thread(target = Game().handler, args = (client_socket,)).start()

# Hand class which dealing out the cards when the game starts
class Hand():
    def __init__(self, gameroom):
        self.hand = hands[gameroom]

    def deal(self, gameroom):
        deck = ["2-S", "3-S", "4-S", "5-S", "6-S", "7-S", "8-S", "9-S", "10-S", "J-S", "Q-S", "K-S", "A-S", "2-C", "3-C", "4-C", "5-C", "6-C", "7-C",
        "8-C", "9-C", "10-C", "J-C", "Q-C", "K-C", "A-C", "2-H", "3-H", "4-H", "5-H", "6-H", "7-H", "8-H", "9-H", "10-H", "J-H", "Q-H", "K-H", "A-H",
        "2-D", "3-D", "4-D", "5-D", "6-D", "7-D", "8-D", "9-D", "10-D", "J-D", "Q-D", "K-D", "A-D"]

        random.shuffle(deck)
        for i in range(13):
            for key in self.hand:
                hands[gameroom][key].append(deck[0])
                del deck[0]

        for players in self.hand:
            h = " ".join(self.hand[players])

            msg = ("\nYour hand:").encode('utf-8')
            buff = f"{len(msg):<{head}}".encode('utf-8')
            players.send(buff + msg)

            msg = (h).encode('utf-8')
            buff = f"{len(msg):<{head}}".encode('utf-8')
            players.send(buff + msg)

# Pile class which handles cards values 
class Pile():
    def __init__(self, card_val):
        self.card_val = card_val

    def check_value(self):
        if self.card_val == "J":
            return 11
        elif self.card_val == "Q":
            return 12
        elif self.card_val == "K":
            return 13
        elif self.card_val == "A":
            return 14
        else:
            return int(self.card_val)

# Rounds class which handles the current round the lobby is in
class Rounds():
    def __init__(self, round):
        self.round = round

    def get_round(self):
        self.round += 1
        return self.round

# Teams class which handles what teams the players are allocated to
class Teams():
    def __init__(self, order):
        self.order = order

    def get_team(self):
        team1 = (self.order[0], self.order[2])
        team2 = (self.order[1], self.order[3])
        return team1, team2

# Game class which handles the main bulk of the game
class Game():
    # First takes players name and assigns them to their chosen lobby
    def handler(self, client_socket):
        global deck
        global deck_backup
        buff = int((client_socket.recv(head)).decode('utf-8').strip())
        name = client_socket.recv(buff).decode('utf-8')

        buff = int((client_socket.recv(head)).decode('utf-8').strip())
        gameroom = client_socket.recv(buff).decode('utf-8')

        msg = (f"{name} has joined the game.").encode('utf-8')

        if gameroom not in gamerooms:
            gamerooms[gameroom] = {}
        gamerooms[gameroom][client_socket] = name

        if gameroom not in hands:
            hands[gameroom] = {}
        hands[gameroom][client_socket] = []
        broadcast(msg, gamerooms[gameroom])

        if gameroom not in turn_order:
            turn_order[gameroom] = []
        turn_order[gameroom].append(client_socket)

        # Waits until lobby has 4 players to start the game
        if len(gamerooms[gameroom]) < 4:
            msg = (f"Waiting for {4-len(gamerooms[gameroom])} more players.").encode('utf-8')
            broadcast(msg, gamerooms[gameroom])

        # After 4 people join, the game starts and players get assigned their teams and hands, nad the trump is chosen
        if len(gamerooms[gameroom]) == 4:

            msg = ("game starting...").encode('utf-8')
            broadcast(msg, gamerooms[gameroom])

            Hand(gameroom).deal(gameroom)
            deck = deck_backup

            team1, team2 = Teams(turn_order[gameroom]).get_team()

            msg = (f"\nTeam 1: ({gamerooms[gameroom][team1[0]]}, {gamerooms[gameroom][team1[1]]})\n").encode('utf-8')
            broadcast(msg, gamerooms[gameroom])

            msg = (f"Team 2: ({gamerooms[gameroom][team2[0]]}, {gamerooms[gameroom][team2[1]]})\n").encode('utf-8')
            broadcast(msg, gamerooms[gameroom])

            score1 = 0
            score2 = 0

            trump = hands[gameroom][team1[0]][0][-1]

            msg = (f"Trump suit: {trump}").encode('utf-8')
            broadcast(msg, gamerooms[gameroom])
            r = 0

            # Game then commences and thirteen rounds play out with each player having 1 turn per round
            for rounds in range(13):
                top = 0
                r = Rounds(r).get_round()
                msg = (f"Round: {r}").encode('utf-8')
                broadcast(msg, gamerooms[gameroom])

                # Whenever a card is played the current leading card is compared
                for turn in range(4):
                    turn_cycle = ("Your turn.").encode('utf-8')
                    buff = f"{len(turn_cycle):<{head}}".encode('utf-8')
                    turn_order[gameroom][turn].send(buff + turn_cycle)

                    buff = int((turn_order[gameroom][turn].recv(head)).decode('utf-8'))
                    msg = turn_order[gameroom][turn].recv(buff).decode('utf-8')

                    card_value = msg[0:-2]

                    if top == 0:
                        card_val = Pile(card_value).check_value()
                        leader = turn_order[gameroom][turn]
                        top = card_val
                        suit = msg[-1]

                    elif (suit == msg[-1]):
                        card_val = Pile(card_value).check_value()
                        if card_val > top:
                            leader = turn_order[gameroom][turn]
                            top = card_val
                            suit = msg[-1]

                    elif (suit != trump) and (msg[-1] == trump):
                        card_val = Pile(card_value).check_value()
                        leader = turn_order[gameroom][turn]
                        top = card_val
                        suit = msg[-1]

                    msg = (gamerooms[gameroom][turn_order[gameroom][turn]] + " > " + msg).encode('utf-8')
                    broadcast(msg, gamerooms[gameroom])

                # After each player gets a turn the round winner is determined
                if leader in team1:
                    score1 += 1
                    msg = ("Team 1 won the round.").encode('utf-8')
                    broadcast(msg, gamerooms[gameroom])
                else:
                    score2 += 1
                    msg = ("Team 2 won the round.").encode('utf-8')
                    broadcast(msg, gamerooms[gameroom])

                msg = (f"Team 1 score: {score1}. Team 2 score: {score2}.").encode('utf-8')
                broadcast(msg, gamerooms[gameroom])

                last = turn_order[gameroom][0]
                turn_order[gameroom].remove(last)
                turn_order[gameroom].append(last)

            # After 13 rounds get played a game winner is determined
            if score1 > score2:
                msg = ("Team 1 wins!").encode('utf-8')
                broadcast(msg, gamerooms[gameroom])
            else:
                msg = ("Team 2 wins!").encode('utf-8')
                broadcast(msg, gamerooms[gameroom])

# Sends message to all players in the chosen lobby
def broadcast(msg, room):
    for sock in room:
        buff = f"{len(msg):<{head}}".encode('utf-8')
        sock.send(buff + msg)

# Basic set-up for server

deck = ["2-S", "3-S", "4-S", "5-S", "6-S", "7-S", "8-S", "9-S", "10-S", "J-S", "Q-S", "K-S", "A-S", "2-C", "3-C", "4-C", "5-C", "6-C", "7-C",
        "8-C", "9-C", "10-C", "J-C", "Q-C", "K-C", "A-C", "2-H", "3-H", "4-H", "5-H", "6-H", "7-H", "8-H", "9-H", "10-H", "J-H", "Q-H", "K-H", "A-H",
        "2-D", "3-D", "4-D", "5-D", "6-D", "7-D", "8-D", "9-D", "10-D", "J-D", "Q-D", "K-D", "A-D"]

deck_backup = deck
gamerooms = {}
addresses = {}
turn_order = {}
hands = {}

ip = "127.0.0.1"
port = 8080

head = 10
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, port))

if __name__ == "__main__":
    server_socket.listen()
    print(f"Game server started on {ip}:{port}")
    new_thread = threading.Thread(target = Server(addresses).connecting)
    new_thread.start()
    new_thread.join()
    server_socket.close()
