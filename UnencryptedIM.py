# Author: Chris Falck
# Date: 8/27/17
# Description: This is a simple unencrypted messenger program that allows messages to be passed to another instance
#   of the program running on a different machine using TCP. The program is configured to operate on port 9456.
# Example command line usage:
#   run >python.exe UnencryptedIM.py -s< on the server machine.
#   run >python.exe UnencryptedIM.py -c serverIPAddr< on the client machine.

import socket
import sys
import select

# Configured by command line flags.
is_server = False
is_client = False
remote_host = ""

# Port number global var used for both the client and host versions of the program.
port = 9456

if sys.argv[1] == "-help" or len(sys.argv) is 1:
    print("Description: This is a simple unencrypted messenger program that allows messages to be passed to another instance\
    \n\tof the program running on a different machine using TCP. The program is configured to \
    \n\toperate on port 9456.")

    print("Example command line usage:\
    \n\trun >python.exe UnencryptedIM.py.py -s< on the server machine.\
    \n\trun >python.exe UnencryptedIM.py.py -c serverIPAddr< on the client machine.")

if sys.argv[1] == "-s":
    is_server = True

if sys.argv[1] == "-c":
    is_client = True
    remote_host = sys.argv[2]

if is_server:

    # Prepare the receiving socket to use IPv4 TCP streaming.
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.bind((socket.gethostname(), port))
    receiving_socket.listen(5)

    possibly_writeable_addrs = []

    while True:
	
	    # Block while we wait for the receiving socket or stdin to become readable.
        ready_receive, ready_write, had_error = \
            select.select([receiving_socket, sys.stdin], [], [], 10)

        for rr in ready_receive:

	        # A message is incoming from the remote socket, so accept the connection,
	        # read the message, and then close the connection. 
            if rr is receiving_socket:
                remote_socket, remote_addr = receiving_socket.accept()

		        # For the server version of this program, we also store incoming connections as possible endpoints
		        # for us to send a message to when the user gives input to sys.stdin.
                already_added = False
                for addr in possibly_writeable_addrs:
                    if remote_addr[0] == addr[0]:
                        already_added = True;
                        break
                if not already_added:
                    possibly_writeable_addrs.append((remote_addr[0], port))
                    print("Current possibilities:", possibly_writeable_addrs)

                msg = remote_socket.recv(4096)
                print(msg.decode())

                remote_socket.close()

	        # A message is incoming from the local sys.stdin aka the user has typed
	        # a message and pressed enter. Read the message from the sys.stdin buffer
	        # and create a new socket to send it to the remote socket.
            if rr is sys.stdin:
                msg = sys.stdin.readline()
                print()

		        # When receiving connections, we store their "from" address as a possible endpoint
		        # to send a message back to. If we fail to send a message to one of these endpoints,
		        # we remove the endpoint address from our list of possible endpoints.
                for p_addr in possibly_writeable_addrs:
                    try:
                        dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        dest_socket.connect(p_addr)
                        dest_socket.sendall(msg.encode())
                        dest_socket.close()
                    except:
                        possibly_writeable_addrs.remove(p_addr)

if is_client:

    # Prepare the receiving socket to use IPv4 TCP streaming.
    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.bind((socket.gethostname(), port))
    receiving_socket.listen(5)

    while True:

	    # Block while we wait for the receiving socket or stdin to become readable.
        ready_receive, ready_write, had_error = \
            select.select([receiving_socket, sys.stdin], [], [], 10)

        for rr in ready_receive:

	        # A message is incoming from the remote socket, so accept the connection,
	        # read the message, and then close the connection.
            if rr is receiving_socket:
                remote_socket, remote_addr = receiving_socket.accept()

                msg = remote_socket.recv(4096)
                print(msg.decode())

                remote_socket.close()

	        # A message is incoming from the local sys.stdin aka the user has typed
	        # a message and pressed enter. Read the message from the sys.stdin buffer
	        # and create a new socket to send it to the remote socket.
            if rr is sys.stdin:
                msg = sys.stdin.readline()
                print()
                dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest_socket.connect((remote_host, port))
                dest_socket.sendall(msg.encode())
                dest_socket.close()

