# General layout and tkinter code modified from https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
import socket
import threading
import sys
import tkinter as tk


def startGameRoom():
    user = Client()
    user.start()

# Sends message to server which in turn sends to all other players in the lobby
def sendMessage(self, err = None):
    global hand
    global cur_suit
    global trump
    global deck
    card = text_entry.get()
    text_entry.delete("0","end")#reset text box

    # Decides if chosen card is a valid play or not
    if card not in hand:
        messages.insert(tk.END, "Card not in hand!\n")

    elif card[-1] != cur_suit and card[-1] != trump and cur_suit != "":
        playable = True
        for i in hand:
            if i[-1] == cur_suit or i[-1] == trump:
                playable = False
        if playable == True:
            hand.remove(card)
            card = card.encode('utf-8')
            buff = f"{len(card):<{head}}".encode('utf-8')
            client_socket.send(buff + card)
        else:
            messages.insert(tk.END, "Must play card from trump's suit or current round's suit!\n")

    # Updates hand removing chosen card
    else:
        hand.remove(card)
        card = card.encode('utf-8')
        buff = f"{len(card):<{head}}".encode('utf-8')
        client_socket.send(buff + card)

# handles bulk of client side functions such as GUI and recieving messages
class Client(threading.Thread):
    def run(self):
        global hand
        global cur_suit
        global trump
        global deck

        global create_title
        global name_title
        global name_frame
        global name_entry_frame
        global name_entry
        global id_frame
        global id_title
        global text_frame
        global text_entry
        global send_frame
        global send_button
        global messages
        global chat_frame
        global messages

        name_text = name_entry.get()
        room_text = id_entry.get()
        name_frame.destroy()
        name_title.destroy()
        name_entry_frame.destroy()
        name_entry.destroy()
        id_frame.destroy()
        id_title.destroy()
        id_entry.destroy()

        client_socket.connect((ip, port))
        name_text = name_text.encode('utf-8')
        buff = f"{len(name_text):<{head}}".encode('utf-8')
        client_socket.send(buff + name_text)

        gameroom = room_text.encode('utf-8')
        buff = f"{len(gameroom):<{head}}".encode('utf-8')
        client_socket.send(buff + gameroom)

        frame = tk.Frame(window,bg="#b71c1c",bd=5) # Design the frame
        frame.place(relx=0.5,rely=0.1,relwidth=0.75, relheight=0.1, anchor="n")# Design the frame

        window.title("Game Room") # Name the window
        create_title = tk.Label(frame, foreground="#fafafa", text ="Game Room",bg="#b71c1c")
        create_title.config(font =("Cooper", 70))
        create_title.pack()

        text_frame = tk.Frame(window,bg="#fafafa",bd=5) # Design the frame for the entry
        text_frame.place(relx=0.50,rely=0.925,relwidth=0.751, relheight=0.05, anchor="n")
        text_entry = tk.Entry(text_frame,font=40) #Instantiate the text_entry box

        text_entry.config(foreground="#D1D2D3",bg="#43a047")
        text_entry.place(relwidth=1,relheight=1)
        text_entry.bind("<Return>", sendMessage)
        send_frame = tk.Frame(window,bg="#2F3136",bd=5) # Design the frame for the buttons
        send_frame.place(relx=0.94,rely=0.91,relwidth=0.10, relheight=0.08, anchor="n")
        send_button = tk.Button(send_frame,text="Send", font=40, command=sendMessage)
        send_button.config(foreground="#D1D2D3",bg="#43a047")
        send_button.place(relx=0,relheight=1,relwidth=1) # Place button


        chat_frame = tk.Frame(window,bg="#fafafa",bd=5) # Design frame for output box
        chat_frame.place(relx=0.5,rely=0.2,relwidth=0.75,relheight=0.7, anchor="n") #place the frame

        messages = tk.Text(chat_frame) # Instantiate the output box
        messages.grid(row=0, column=0, padx=10, pady=10)
        messages.config(foreground="#fafafa",bg="#36393F")
        messages.place(relwidth=1,relheight=1) #Place the output box

        # Takes messages from server and displays them in the GUI
        counter = 0
        begun = False
        while True:
            try:
                buff = int((client_socket.recv(head)).decode('utf-8'))
                msg = client_socket.recv(buff).decode('utf-8')

                if msg.split(" ")[0] == "Trump":
                    trump = msg[-1]

                elif len(msg.split(" ")) == 13:
                    hand = msg.split(" ")

                elif msg.split(" ")[-1] in deck and counter == 0:
                    cur_suit = msg[-1]
                    counter += 1
                    messages.insert(tk.END, f"Round suit: {cur_suit}\n")

                elif msg.split(" ")[-1] in deck and (0 < counter < 4):
                    counter += 1

                if counter == 4:
                    cur_suit = ""
                    counter = 0

                messages.insert(tk.END, msg+"\n")

                if msg[:12] == "Team 1 score":
                    messages.insert(tk.END, "Your hand:")
                    messages.insert(tk.END, " ".join(hand))
                    messages.insert(tk.END, "\n" + "")

            except OSError:
                break


def main():
    global create_title
    global name_title
    global name_frame
    global name_entry_frame
    global name_entry
    global id_frame
    global id_title
    global room_frame
    global id_entry
    global join_room_frame
    global join_button

    window.title("Main Menu") # Name the window
    frame = tk.Frame(window,bg="#b71c1c",bd=5) # Design the frame
    frame.place(relx=0.5,rely=0.1,relwidth=0.75, relheight=0.1, anchor="n")
    window.configure(bg="#2F3136")
    l = tk.Label(frame, foreground="#fafafa", text ="WELCOME TO WHIST",bg="#b71c1c")
    l.config(font =("Cooper", 70))
    l.pack()

    name_frame = tk.Frame(window,bg="#b71c1c",bd=5) # Design the frame for the title
    name_frame.place(relx=0.5,rely=0.3,relwidth=0.25, relheight=0.05, anchor="n")
    name_title = tk.Label(name_frame, foreground="#D1D2D3", text ="Enter your username:",bg="#b71c1c")
    name_title.config(font =("Cooper", 30))
    name_title.pack()

    name_entry_frame = tk.Frame(window,bg="#f44336",bd=5) # Design the frame for the entry
    name_entry_frame.place(relx=0.5,rely=0.35,relwidth=0.18, relheight=0.05, anchor="n")
    name_entry = tk.Entry(name_entry_frame,font=40) #Instantiate the name_entry box
    name_entry.config(foreground="#fafafa",bg="#36393F")
    name_entry.place(relwidth=1,relheight=1)

    id_frame = tk.Frame(window,bg="#b71c1c",bd=5) # Design the frame for the id text
    id_frame.place(relx=0.5,rely=0.50,relwidth=0.18, relheight=0.05, anchor="n")
    id_title = tk.Label(id_frame, foreground="#fafafa", text ="Enter room ID:",bg="#b71c1c")
    id_title.config(font =("Cooper", 30))
    id_title.pack()

    room_frame = tk.Frame(window,bg="#f44336",bd=5) # Design the frame for the entry
    room_frame.place(relx=0.5,rely=0.55,relwidth=0.18, relheight=0.05, anchor="n")
    id_entry = tk.Entry(room_frame,font=40) #Instantiate the id_entry box
    id_entry.config(foreground="#fafafa",bg="#36393F")
    id_entry.place(relwidth=1,relheight=1)

    join_room_frame = tk.Frame(window,bg="#00c853",bd=5) # Design the frame for the buttons
    join_room_frame.place(relx=0.5,rely=0.75,relwidth=0.20, relheight=0.1, anchor="n")
    join_button = tk.Button(join_room_frame,text="Join", font=40, bg="blue", command=startGameRoom)# Instantiate button
    join_button.config(foreground="#00c853",bg="#00c853")
    join_button.place(relx=0,relheight=1,relwidth=1) # Place button

    window.mainloop() #Start window


if __name__ == '__main__':
    suit = False
    cur_suit = ""
    trump = ""
    deck = ["2-S", "3-S", "4-S", "5-S", "6-S", "7-S", "8-S", "9-S", "10-S", "J-S", "Q-S", "K-S", "A-S", "2-C", "3-C", "4-C", "5-C", "6-C", "7-C",
            "8-C", "9-C", "10-C", "J-C", "Q-C", "K-C", "A-C", "2-H", "3-H", "4-H", "5-H", "6-H", "7-H", "8-H", "9-H", "10-H", "J-H", "Q-H", "K-H", "A-H",
            "2-D", "3-D", "4-D", "5-D", "6-D", "7-D", "8-D", "9-D", "10-D", "J-D", "Q-D", "K-D", "A-D"]

    ip = "127.0.0.1"
    port = 8080

    head = 10
    hand = []

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HEIGHT = 1080 # Set the height of the gui
    WIDTH = 1920 # Set the width of the gui
    window = tk.Tk() #instantiate the window
    canvas = tk.Canvas(window, height=HEIGHT,width=WIDTH,bg="#b71c1c") #design the window
    canvas.pack()
    main()
