#!/usr/bin/env python3

import socket
import threading
import time
import pickle

HOST_SERVER = ''  # Use '127.0.0.1' for localhost. Use '' for outside host.
PORT_SERVER = 51232  # The port used by the server

dictionary_of_connections = {}  # Maintains the record of connected clients
                                # Structure: {client_addr_str: client_conn_object}
number_of_connected_clients = 0

maximum_allowed_players = None

type_of_player = ""

def network_receive(socket_object, size=1024):
    '''
    Receives message_object from network.
    :param socket_object: Socket that receives the data_object.
    :param size: Size of message_object. Defaults to 1024 bytes.
    :return: message_object that is obtained after loading the received pickle from the network.
    '''
    try:
        message_object = pickle.loads(socket_object.recv(size))
    except EOFError as e:
        print("EOFError. Program will continue.")
        return b''
    return message_object


def network_send(socket_object, message_object):
    '''
    Sends message_object to the network.
    :param socket_object: Socket object through message_object is sent.
    :param message_object: The object that is pickled and sent to the network.
    :return: None
    '''
    socket_object.sendall(pickle.dumps(message_object))


def threaded_client(conn, lock):
    '''
    Handles each client separately (as a new thread).
    :param conn: Client socket connection object.
    :param lock: Lock object for safety against race condition.
    :return: None
    '''

    global dictionary_of_connections
    global number_of_connected_clients
    global type_of_player
    global maximum_allowed_players
    all_players_joined = False
    with conn:
        while True:
            data = network_receive(conn)  # Message received from client.
            client_addr_str = str(conn.getpeername()[0])+'_'+str(conn.getpeername()[1])
            print("Received <", data, "> from client <", client_addr_str,"> @ ", str(time.time()))
            if not data:  # break if b'' is received from client.
                if number_of_connected_clients == 1:  # The last client also disconnected
                    number_of_connected_clients = 0
                    print("Client <", client_addr_str, "> disconnected. Number of connected clients = ", number_of_connected_clients)
                    dictionary_of_connections.clear()
                break
            if not all_players_joined:
                parts_of_data = len(data.split('_'))
                type_of_player = parts_of_data[0]
                maximum_allowed_players = int(parts_of_data[1])
                print(f'server: parts_of_data = {parts_of_data}')
            else:
                for client_addr_str in dictionary_of_connections:
                    client_conn = dictionary_of_connections[client_addr_str]
                    if client_conn is not conn:  # Message of a client is sent to all other clients but not to itself.
                        try:
                            if dictionary_of_connections[client_addr_str] is not None:
                                network_send(client_conn, data)
                                print("Sending <", data, "> to client <", client_addr_str, "> @ ", str(time.time()))
                        except:
                            number_of_connected_clients -= 1
                            print('Client <', client_addr_str, "> disconnected. Number of connected clients = ", number_of_connected_clients)
                            lock.acquire()
                            dictionary_of_connections[client_addr_str] = None  # Disconnected clients connections are set to None
                                                                               # Not popped off to prevent updates while iteration.
                            lock.release()


def main():
    '''
    Accepts clients' connections. Every client is handled by a separate thread (threaded_client).
    Responding to clients is handled in the same thread.
    :return:None
    '''
    global dictionary_of_connections
    global number_of_connected_clients
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        lock = threading.Lock()  # Safety against race condition, as the thread(threaded_client) uses a global variable.
        s.bind((HOST_SERVER, PORT_SERVER))
        s.listen()
        print("Server started.")
        while True:
            print("Waiting for connection ...")
            conn, addr = s.accept()
            number_of_connected_clients += 1
            print("Connected to new client <", addr, ">. Number of connected clients = ", number_of_connected_clients)
            addr_str = str(addr[0])+'_'+str(addr[1])
            if addr_str not in dictionary_of_connections:
                dictionary_of_connections.update({addr_str: conn}) # Update the record of clients
                if number_of_connected_clients == 1:
                    player_type = "host"
            t = threading.Thread(target=threaded_client, args=(conn, lock))
            t.start()
        t.join()


if __name__ == "__main__":
    main()