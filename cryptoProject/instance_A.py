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


shared_symmetric = "samplkey"
public_B = None
n_B = None
p, q = RSA.generate_prime(100,500), RSA.generate_prime(100, 500)
while p == q:
    q = RSA.generate_prime(100,500)

n = p * q
phi = (p - 1) * (q - 1)
public_A =  random.randint(3, phi - 1)
while math.gcd(public_A, phi)!= 1:
    public_A = random.randint(3, phi - 1)
private_A = RSA.mod_inverse1(public_A, phi)

event_get_key_A = threading.Event()
event_send_key_A = threading.Event()


app = Flask(__name__)
###server_ready = threading.Event()


#event_send_key_B = threading.Event()

#event_get_key_B = threading.Event()
#event_gui_start = threading.Event()









@app.route('/hand_shake_A',methods=['POST'])
def get_key():
    global public_B
    global n_B
    data = request.get_json()
    n_B = data.get("n","")
    public_B = data.get("message","")
    print("public B received: ", public_B)
    # Signal that A is ready to send its key
    event_get_key_A.set()
    #event_send_key_B.clear()
    send_key()  # Step 3
    return ("end get_key")


def send_key():
    event_get_key_A.wait()
    url = "http://127.0.0.1:5001/hand_shake_B"
    encoded_symmetric = [ord(ch) for ch in shared_symmetric]
    encode = [pow(ch, public_B, n_B) for ch in encoded_symmetric]
    print("encoded share symmetric: ", encode)
    response = requests.post(url,json={"message": encode})
    print("key sent to B")
    event_send_key_A.set()  # Signal that the key has been sent



def start_server():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    print("Flask server started successfully.")




# Flask route for receiving messages
@app.route('/receive_message', methods=['POST'])
def receive_message():
    data = request.get_json()
    message = data.get("message", "")
    #received_key = data.get("key",None)


    #decrypt process
    key_bits = DES.str_to_bits(shared_symmetric)[:64]
    subkeys = DES.key_schedule(key_bits)
    decrypted_bits = DES.des_decrypt_block(message, subkeys)
    decrypted_padded_text = DES.bits_to_str(decrypted_bits)
    decrypted_text = DES.unpad(decrypted_padded_text)

    display_message(f"Instance B: {decrypted_text}")
    return "Message received!"


def send_message(msg):
    url = "http://127.0.0.1:5001/receive_message"  # Change port for Instance B
    padded_plaintext = DES.pad(msg)
    plaintext_bits = DES.str_to_bits(padded_plaintext)

    key_bits = DES.str_to_bits(shared_symmetric)[:64]
    subkeys = DES.key_schedule(key_bits)
    cipher = DES.des_encrypt_block(plaintext_bits, subkeys)
    payload = {
        "message": cipher,
        "key": shared_symmetric
    }
    try:
        response = requests.post(url, json= payload)
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
    root.title("Instance A - Messaging App")

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
    # Wait for Instance B to send its key
    #event_send_key_B.wait()
    event_send_key_A.wait()  # Signal that the key has been sent
    # Create and run the GUI
    gui = create_gui()
    gui.mainloop()
