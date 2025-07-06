from flask import Flask, request, jsonify
import threading
import requests
import tkinter as tk
from tkinter import scrolledtext
import os
import signal
import DES
import RSA
import random
import math
import time


# Declare global variable
#share_key = "samplkey"
#key_bits = DES.str_to_bits(share_key)[:64]
#subkeys = DES.key_schedule(key_bits)
#server_ready = threading.Event()
shared_symmetric = None
#shared_symmetric = "samplkey"
p, q = RSA.generate_prime(100,500), RSA.generate_prime(100, 500)
while p == q:
    q = RSA.generate_prime(100,500)

n = p * q
phi = (p - 1) * (q - 1)
public_B =  random.randint(3, phi - 1)
while math.gcd(public_B,phi)!= 1:
    public_B = random.randint(3, phi - 1)
private_B = RSA.mod_inverse1(public_B, phi)
print("public B : ",public_B)

event_send_key_B = threading.Event()
event_get_key_B = threading.Event()

app = Flask(__name__)


def send_key():
    url = "http://127.0.0.1:5000/hand_shake_A"
    payload ={
        "message": public_B,
        "n": n
    }
    response = requests.post(url, json=payload)
    print("public key sent to A",public_B)
    event_send_key_B.set()  # Signal that B has sent its key


@app.route('/hand_shake_B',methods=['POST']) #listen and triggers automatically
def get_key():
    time.sleep(5)
    global shared_symmetric
    data = request.get_json()
    shared = data.get("message","")
    print("the encoded share symmetric: ",shared)
    # message_encoded = [pow(ch,d,n) for ch in cipher]
    share_decoded = [pow(ch, private_B, n) for ch in shared]
    shared_symmetric = "".join(chr(ch) for ch in share_decoded)
    print("shred key received from A: ",shared_symmetric)
    event_get_key_B.set()  # Signal that Instance B has received the key
    return "Shared symmetric key received!"


def start_server():
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
    print("Flask server started successfully.")


# Flask route for receiving messages
@app.route('/receive_message', methods=['POST'])
def receive_message():
    data = request.get_json()
    message = data.get("message", "")
    #received_key = data.get("key",None)
    key_bits = DES.str_to_bits(shared_symmetric)[:64]
    subkeys = DES.key_schedule(key_bits)
    #decrypt process

    decrypted_bits = DES.des_decrypt_block(message, subkeys)
    decrypted_padded_text = DES.bits_to_str(decrypted_bits)
    decrypted_text = DES.unpad(decrypted_padded_text)
    display_message(f"Instance B: {decrypted_text}")
    return "Message received!"


def send_message(msg):
    url = "http://127.0.0.1:5000/receive_message"  # Change port for Instance B

    # Encrypt using DES
    #share_key = "samplkey"
    #key_bits = DES.str_to_bits(share_key)[:64]
    #subkeys = DES.key_schedule(key_bits)
    padded_plaintext = DES.pad(msg)
    plaintext_bits = DES.str_to_bits(padded_plaintext)
    key_bits = DES.str_to_bits(shared_symmetric)[:64]
    subkeys = DES.key_schedule(key_bits)
    cipher_b = DES.des_encrypt_block(plaintext_bits, subkeys)
    payload = {
        "message": cipher_b,
        "key": shared_symmetric
    }

    try:
        response = requests.post(url, json=payload)
        display_message(f"Me: {msg}")
    except requests.exceptions.ConnectionError:
        display_message("Could not connect to Instance B. Is it running?")




# Function to terminate the server and close the GUI
def terminate_instance():
    os.kill(os.getpid(), signal.SIGINT)

# GUI Components
def display_message(msg):
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, msg + "\n")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)

def on_send_click():
    message = message_entry.get()
    if message:
        send_message(message)
        message_entry.delete(0, tk.END)


def create_gui():
    global chat_log, message_entry

    root = tk.Tk()
    root.title("Instance B - Messaging App")

    # Chat log area
    chat_log = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20, width=50)
    chat_log.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Message entry
    message_entry = tk.Entry(root, width=40)
    message_entry.grid(row=1, column=0, padx=10, pady=10)

    # Send button
    send_button = tk.Button(root, text="Send", command=on_send_click)
    send_button.grid(row=1, column=1, padx=10, pady=10)

    # Exit button
    exit_button = tk.Button(root, text="Exit", command=terminate_instance)
    exit_button.grid(row=2, column=0, columnspan=2, pady=10)

    return root

# Main block
if __name__ == "__main__":
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    # Send the key to Instance A (Step 1)
    send_key()

    # Wait for Instance A to send back its key

    # Wait for Instance A to send back its key
    event_get_key_B.wait()  # Signal that Instance B has received the key

    # Delay to ensure the server is up before sending the key


    # Execute the function after server starts
    #exchange_key()
    #receive_symmetric()
    # Create and run the GUI
    gui = create_gui()
    gui.mainloop()
