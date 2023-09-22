import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back

# init colors
init()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

# choose a random color for the client
client_color = random.choice(colors)

# server's IP address
# if the server is not on this machine, 
# put the private (network) IP address (e.g 192.168.1.2)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002 # server's port
separator_token = "<SEP>" # we will use this to separate the client name & message
cipher = ''
message = ''
key = ''

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")
help = "help:    /h \nexit: /q \ndecrypt: /d \nencrypt: /e"
print(help)
# prompt the client for a name
name = input("Enter your name: ")
notify = f"{name} has connected."
if notify:
    s.send(notify.encode())   

alphabet = "abcdefghijklmnopqrstuvwxyz "
letter_to_index = dict(zip(alphabet, range(len(alphabet))))
index_to_letter = dict(zip(range(len(alphabet)), alphabet))

class Vigenere:
    def __init__(self, message, key, cipher):
        self.message = message
        self.key = key
        self.cipher = cipher

    def encrypt(self):
        #to encrypt:
        #enciphered index = (plaintext index + keyword index) mod 26
        encrypted = ""
        #split the message to the length of the key
        split_message = [self.message[i : i + len(self.key)] for i in range(0, len(self.message), len(key))]
        #convert the message to index and add the key (mod 26)
        for each_split in split_message:
            i = 0
            for letter in each_split:
                number = (letter_to_index[letter] + letter_to_index[self.key[i]]) % len(alphabet)
                encrypted += index_to_letter[number]
                i += 1

        return encrypted

    def decrypt(self):
        #to decrypt:
        #deciphered index = (cipher index - keyword index) mod 26
        decrypted = ""
        #split the message to the length of the key
        split_encrypted = [self.cipher[i : i + len(self.key)] for i in range(0, len(self.cipher), len(self.key))]
        #convert the cipher to index and saubtract the key (mod 26)
        for each_split in split_encrypted:
            i = 0
            for letter in each_split:
                number = (letter_to_index[letter] - letter_to_index[self.key[i]]) % len(alphabet)
                decrypted += index_to_letter[number]
                i += 1

        return decrypted

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print("\n" + message)

# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

def send_message(key, message):
    o1 = Vigenere(message, key, cipher)
    encrypted_message = o1.encrypt()
    # add the datetime, name & the color of the sender
    # encrypt and send the formatted message
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    format_message = f"{client_color}[{date_now}] {name}{separator_token}{encrypted_message}{Fore.RESET}"
    # s.send(to_send.encode())
    s.send(format_message.encode())

def decrypt_message(key, cipher):
    o2 = Vigenere(message, key, cipher)
    decrypted_message = o2.decrypt()
    print(f"decrypted message: {decrypted_message}")

while True:
    # input message we want to send to the server
    to_send = input()
    # a way to exit the program
    if to_send.lower() == '/q':
        print('exiting program')
        break
    elif to_send.lower() == '/d':
        cipher = input("input encrypted message: ")
        if cipher:
            key = input("please enter an encryption key: ")
            decrypt_message(key, cipher)
    else:
        key = input("please enter an encryption key: ")
        message = to_send.lower()
        send_message(key, message)

# close the socket
s.close()