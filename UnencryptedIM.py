# Author: Chris Falck
# Date: 8/27/17
# Description: This is a simple unencrypted messenger program that allows messages to be passed to another instance
#   of the program running on a different machine using TCP. The program is configured to
#   operate on port 9999.
# Example command line usage:
#   run >python.exe UnencryptedIM.py -s< on the server machine.
#   run >python.exe UnencryptedIM.py -c serverIPAddr< on the client machine.

import socket
import sys
import threading
import os

# Configured by command line flags.
is_server = False
is_client = False
remote_host = ""

if len(sys.argv) is 1:
    print("Please provide -s or -c to indicate client or server mode.")
    exit()

if sys.argv[1] == "-help":
    print("Description: This is a simple unencrypted messenger program that allows messages to be passed to another instance\
    \n\tof the program running on a different machine using TCP. The program is configured to \
    \n\toperate on port 9999.")

    print("Example command line usage:\
    \n\trun >python.exe UnencryptedIM.py -s< on the server machine.\
    \n\trun >python.exe UnencryptedIM.py -c serverIPAddr< on the client machine.")

if sys.argv[1] == "-s":
    is_server = True

if sys.argv[1] == "-c":
    is_client = True
    try:
        remote_host = sys.argv[2]
    except:
        # Default to a known IP address if the user did not specify one.
        remote_host = "192.168.1.165"

def sending_thread(remote_addr):
    while True:
        # Open connection.
        dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest_socket.connect((remote_addr, 9999))

        # Collect user input.
        msg = input()

        # Send input and close connection.
        dest_socket.sendall(msg.encode())
        dest_socket.close()

        if msg == "exit()":
            os._exit(1)

def receiving_thread():
    # Track whether or not we've already created a sending_thread for server instances of this program.
    remote_host_connected = False

    # Prepare the receiving socket to use IPv4 TCP streaming.
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.bind((socket.gethostname(), 9999))
    receiving_socket.listen()

    while True:
        # Wait for an incoming connection.
        client_socket, client_addr = receiving_socket.accept()

        # If this program is a server and this is the first message we have received, set up a sending_thread
        # pointed at the address we received a message from so we can send messages back.
        if is_server and remote_host_connected is not True:
            remote_host_connected = True
            threading.Thread(target=sending_thread, args=[client_addr[0]]).start()

        msg = client_socket.recv(4096)
        print(msg.decode())
        client_socket.close()

        if msg.decode() == "exit()":
            os._exit(1)

if is_server:
    # print(socket.getaddrinfo(socket.gethostname(), 9999))  # DEV.

    # Set up a receiver but don't attempt to connect to any remote hosts yet.
    threading.Thread(target=receiving_thread).start()

if is_client:
    # Set up a receiver, and then attempt to connect the sender to a remote host.
    threading.Thread(target=receiving_thread).start()
    threading.Thread(target=sending_thread, args=[remote_host]).start()
