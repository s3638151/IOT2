import socket
import project_constant
import logging
import json
import time

from consolemenu import *
from consolemenu.items import *


def unlock_car():
    """It is a function to unlock a car

    To collect user inputs, then connect mp_listener through a socket connection
    transfer use inputs in json format.

    Get response from mp_listener from socket and parse information and display
    to user.


    Returns:
        No return value

    """

    #collect user inputs
    logging.info('unlock a car')
    username = input("please input you username:")
    password = input("please input you password:")
    car_id = input("please input car id:")

    #connect mp_listener via a socket connection
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((project_constant.ProjectConst.ListenerIP,project_constant.ProjectConst.ListenerPort))
    #transfer request in json format
    data = {'username':username, 'password':password, 'car_id':car_id,'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'action':'unlock'}
    str_json = json.dumps(data)
    client.send(str_json.encode())
    #get response from mp
    str_recv = client.recv(1024).strip().decode()
    logging.debug(str_recv)
    recv_data = json.loads(str_recv)
    logging.debug(recv_data)
    #parse response
    if (recv_data['status']==0):
        print("successfully unlocked the car!")
    else:
        print(recv_data['message'])

    input("please any key to return menu:")

def return_car():
    """It is a function to return a car

    To collect user inputs, then connect mp_listener through a socket connection
    transfer use inputs in json format.

    Get response from mp_listener from socket and parse information and display
    to user.


    Returns:
        No return value

    """
    #collect user inputs
    logging.info('return a car')
    username = input("please input you username:")
    password = input("please input you password:")
    rent_id = input("please input rent id:")

    #connect mp_listener via a socket connection
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((project_constant.ProjectConst.ListenerIP,project_constant.ProjectConst.ListenerPort))
    #transfer request in json format
    data = {'username':username, 'password':password,'rent_id':rent_id,'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'action':'return'}
    str_json = json.dumps(data)
    client.send(str_json.encode())
    #get response from mp
    str_recv = client.recv(1024).strip().decode()
    logging.debug(str_recv)
    #parse response
    recv_data = json.loads(str_recv)
    if (recv_data['status']==0):
        print("successfully returned the car!")
    else:
        print(recv_data['message'])

    logging.debug(recv_data)

    input("please any key to return menu:")

def create_menu():
    """It is a function to create a consolemenu libary menu object

    To create a menu object and add respective fuction items

    Returns:
        return a consolemenu libary menu object.


    """
    menu = ConsoleMenu("Console-based system on AP")
    function_item = FunctionItem("Unlock a car", unlock_car)
    menu.append_item(function_item)
    function_item = FunctionItem("Return a car", return_car)
    menu.append_item(function_item)


    return menu



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(levelname)s<%(module)s>: %(message)s', level=logging.DEBUG)
    logging.info('starting ap_console...')

    menu = create_menu()

    menu.show()
