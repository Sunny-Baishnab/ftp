from ipaddress import ip_address
import socket
from threading import Thread
import time
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

IP_ADDRESS = '127.0.0.1'
PORT = 8000

SERVER = None
CLIENTS = {}
BUFFER_SIZE = 4096

is_dir_exist = os.path.isdir('shared_files')
if(not is_dir_exist):
    os.mkdir('shared_files')

def accept_connections():
    global SERVER
    global CLIENTS
    
    while True:
        client,addr = SERVER.accept()
        clientName = client.recv(4096).decode().lower()
        CLIENTS[clientName] = {
            'client':client,
            'address':addr,
            'connected_with': '',
            'file_name': '',
            'file_size': 4096
        }
        print(f'connection established with {clientName}:{addr}')
        thread = Thread(target = handleClient, args = (client,clientName))
        thread.start()

def handleClient(client,clientName):
    global SERVER
    global BUFFER_SIZE
    global CLIENTS

    banner1 = 'Welcome you are now connected to server\nClick on refresh button to see all available users\nClick on connect to start chatting'
    client.send(banner1.encode())

    while True:
        try:
            BUFFER_SIZE = CLIENTS[clientName]['file_size']
            chunk = client.recv(BUFFER_SIZE)
            message = chunk.decode().strip().lower()
            if(message):
                handleMessages(client,message,clientName)
        except:
            pass



def handleMessages(client,message,clientName):
    if(message == 'show list'):
        handleShowList(client)
    elif(message[:7]=='connect'):
        connect_client(message,client,clientName)
    elif(message[:10]=='disconnect'):
        disconnect_client(message,client,clientName)
    elif(message[:4]=='send'):
        fileName = message.split(' ')[1]
        a = message.split(' ')[2]
        fS = int(a)
        handle_send_files(clientName,fileName,fS)
        print(clientName+' '+fileName+' '+fS)
    elif(message  == 'y' or message == 'Y'):
        grantAccess(clientName)
    elif(message == 'n' or message == 'N'):
        declineAccess(clientName)
    else:
        connected = CLIENTS[clientName]['connected_with']
        if(connected):
            sendTextMessage(clientName,message)
        else:
            handleErrorMessage(client)

def handleShowList(client):
    global CLIENTS

    counter = 0
    for c in CLIENTS :
        counter+=1
        client_address = CLIENTS[c]['address'][0]
        connected_with = CLIENTS[c]['connected_with']
        message = ''
        if(connected_with): 
            message = f"{counter},{c},{client_address}, connected with {connected_with},tiul,\n" 
        else: 
            message = f"{counter},{c},{client_address}, Available,tiul,\n" 

        client.send(message.encode()) 
        time.sleep(1)

def connect_client(msg,client,clientName):
    global CLIENTS

    enteredClientName = msg[8:].strip()
    if(enteredClientName in CLIENTS):
        if(not CLIENTS[clientName]['connected_with']):
            CLIENTS[enteredClientName]['connected_with'] = clientName
            CLIENTS[clientName]['connected_with'] = enteredClientName

            otherClientSocket = CLIENTS[enteredClientName]['client']
            greet_msg = f'Hello,{enteredClientName} {clientName} is connected with you'
            otherClientSocket.send(greet_msg.encode())

            message = f'You have successfully connected with {enteredClientName}'
            client.send(message.encode())
        else:
            otherClientName = CLIENTS[clientName]['connected_with']
            message = f'You are already connected with {otherClientName}'
            client.send(message.encode())

def disconnect_client(msg,client,clientName):
    global CLIENTS

    enteredClientName = msg[11:].strip()
    if(enteredClientName in CLIENTS):
        CLIENTS[enteredClientName]['connected_with'] = ''
        CLIENTS[clientName]['connected_with'] = ''

        otherClientSocket = CLIENTS[enteredClientName]['client']
        greet_msg = f'Hello,{enteredClientName} {clientName} is disconnected with you'
        otherClientSocket.send(greet_msg.encode())

        message = f'You have successfully disconnected with {enteredClientName}'
        client.send(message.encode())

def handleErrorMessage(client):
    message = '''you need to connect with one of the clients first before sending any message\nclick on refresh to see all available users'''
    client.send(message.encode())

def sendTextMessage(clientName,message):
    global CLIENTS
    otherClientName = CLIENTS[clientName]['connected_with']
    otherClientSocket = CLIENTS[otherClientName]['client']
    final_message = clientName+'>'+message
    otherClientSocket.send(final_message.encode())

def setup():
    print('IP Messenger')

    global PORT 
    global IP_ADDRESS
    global SERVER

    SERVER = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    SERVER.bind((IP_ADDRESS,PORT))

    SERVER.listen(100)

    print('server is waiting for incoming connection')
    accept_connections()

def ftp():
    global IP_ADDRESS
    authorizer = DummyAuthorizer()
    authorizer.add_user('lftpd','lftpd','.',perm = 'elradfmw')
    handler = FTPHandler
    handler.authorizer  = authorizer
    FTP_Server = FTPServer((IP_ADDRESS,21),handler)
    FTP_Server.serve_forever()

def grantAccess(clientName):
    global CLIENTS
    other_client_name = CLIENTS[clientName]['connected_with']
    other_client_socket = CLIENTS[other_client_name]['client']
    message = 'access granted'
    other_client_socket.send(message.encode())

def declineAccess(clientName):
    global CLIENTS
    other_client_name = CLIENTS[clientName]['connected_with']
    other_client_socket = CLIENTS[other_client_name]['client']
    message = f'sorry! {clientName} declined your request.'
    other_client_socket.send(message.encode())

def handle_send_files(clientName,fileName,file_Size):
    global CLIENTS
    CLIENTS[clientName]['file_name'] = fileName
    CLIENTS[clientName]['file_size'] = file_Size
    other_clients_name = CLIENTS[clientName]['connected_with']
    other_clients_socket = CLIENTS[other_clients_name]['client']
    message = f'\n {clientName} wants to send {fileName} file with size {file_Size} bytes.\n do you want to download ? y/n'
    other_clients_socket.send(message.encode())
    time.sleep(1)
    messageDown = f'download:{fileName}'
    other_clients_socket.send(messageDown.encode())


setup_thread = Thread(target = setup)
setup_thread.start()
ftp_thread = Thread(target = ftp)
ftp_thread.start()