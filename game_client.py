#!/usr/bin/env python3

import socket
import time
import threading
import pickle

received_message = None

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


def receiving_threaded(s):
    global received_message
    '''
    Receives messages from the server, anytime. This thread is useful when data from server is expected anytime.
    :param s: Socket object that connects to the server.
    :return: None
    '''
    with s:
        while True:
            received_message = network_receive(s)
            if not received_message:
                break


def main():
    '''
    Connects to server and sends "Hello, world" every 5 seconds.
    Receiving is handled by a separate thread (receiving_thread)
    :return: None
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST_CLIENT, PORT_CLIENT))
        k = 0  # Non-mandatory counter to track of number of times messages are sent.
        t1 = time.time()
        t = threading.Thread(target=receiving_threaded, args=(s,))
        t.start()
        time.sleep(5)  # Non-mandatory delay before client begins to send messages
        while True:
            t2 = time.time()
            if t2 - t1 > 5:  # Send messages in an interval of 5 seconds
                k = k + 1
                print(f'k = {k}: ', end="")
                t1 = t2
                message_string = "Act now"
                print("Sending <", message_string, "> to server <", str(HOST_CLIENT)+'_'+str(PORT_CLIENT), "> @ ", str(time.time()))
                network_send(s, message_string)
                time.sleep(0.01)  # Precautionary delay for received_message to get teh message in receiving_threaded.
                print(f'received_message = {received_message}')
        t.join()


if __name__ == "__main__":
    main()
