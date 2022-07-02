import socket
from threading import Thread
from tkinter import *
from tkinter import ttk
import ftplib
from ftplib import FTP
import os
import ntpath
import time
from tkinter import filedialog
from pathlib import Path

IP_ADDRESS = '127.0.0.1'
PORT = 8000

SERVER = None

name = None
list_box = None
text_area = None
label_chat = None
text_message = None

BUFFER_SIZE = 4096

sending_file = None
downloading_file = None
file_to_download = None

def open_chat_window():
    print('IP_MESSANGER')

    window = Tk()
    window.title('MESSENGER')
    window.geometry('500x350')

    global name
    global list_box
    global text_area
    global label_chat
    global text_message
    global filePathLabel

    name_label = Label(window,text = 'Enter Your Name',font = ('Calibri',10))
    name_label.place(x = 10,y = 8)

    name = Entry(window,width = 30,font = ('Calibri',10))
    name.place(x = 120,y = 8)
    name.focus()

    connect_server = Button(window,text = 'Connect to Chat Server',bd = 1, font = ('Calibri',10),command=connect_to_server)
    connect_server.place(x = 350,y = 6)

    separater = ttk.Separator(window,orient = 'horizontal')
    separater.place(x =0,y= 35,relwidth = 1,height = 0.1)

    label_users = Label(window,text = 'Active Users', font = ('Calibri',10))
    label_users.place(x = 10,y = 50)

    list_box = Listbox(window,width = 67,height = 5,font = ('Calibri',10),activestyle='dotbox')
    list_box.place(x = 10,y = 70)

    scroll_bar1 = Scrollbar(list_box)
    scroll_bar1.place(relheight=1,relx = 1)
    scroll_bar1.config(command = list_box.yview)

    connect = Button(window,text = 'Connect',bd = 1,font = ('Calibri',10),command=connect_with_client)
    connect.place(x = 282,y = 160)

    disconnect = Button(window,text = 'Disconnect',bd = 1,font = ('Calibri',10),command=disconnect_with_client)
    disconnect.place(x = 350,y = 160)

    refresh = Button(window,text = 'Refresh',bd = 1,font = ('Calibri',10),command = showClientsList)
    refresh.place(x = 435,y = 160)

    label_chat = Label(window,text = 'Chat Window', font = ('Calibri',10))
    label_chat.place(x = 10,y = 180)

    text_area = Text(window,width = 67,height = 6,font = ('Calibri',10))
    text_area.place(x = 10,y = 200)

    scroll_bar2 = Scrollbar(text_area)
    scroll_bar2.place(relheight=1,relx = 1)
    scroll_bar2.config(command = text_area.yview)

    attach_button = Button(window,text = '  Attach ',bd = 1,font = ('Calibri',10),command = browseFiles)
    attach_button.place(x = 10,y = 305)

    text_message = Entry(window,width = 43,font = ("Calibri",13))
    text_message.pack()
    text_message.place(x = 98,y = 306)

    send_button = Button(window,text = ' Send',bd = 1,font = ('Calibri',10),command = sendMessage)
    send_button.place(x = 450,y = 305)



    filePathLabel = Label(window,text = '',font = ('Calibri',8),fg = 'red')
    filePathLabel.place(x = 10,y = 330)

    window.mainloop()

def receive_message():
    global SERVER
    global BUFFER_SIZE
    global name
    global text_area
    global downloading_file
    global file_to_download

    while True:
        chunk = SERVER.recv(BUFFER_SIZE)
        try:
            if("tiul" in chunk.decode() and "1.0," not in chunk.decode()):
                letter_list = chunk.decode().split(",")
                list_box.insert(letter_list[0],letter_list[0]+":"+letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
                print(letter_list[0],letter_list[0]+":"+letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
            elif(chunk.decode()=='access granted'):
                label_chat.configure(text = '')
                text_area.insert(END,'\n'+chunk.decode('ascii'))
                text_area.see('end')
            elif(chunk.decode() == 'sorry! client declined your request.'):
                label_chat.configure(text = '')
                text_area.insert(END,'\n'+chunk.decode('ascii'))
                text_area.see('end')
            elif('download ?' in chunk.decode()):
                downloading_file = chunk.decode('ascii').split(' ')[4].strip()
                BUFFER_SIZE = int(chunk.decode('ascii').split(' ')[9])
                text_area.insert(END,'\n'+chunk.decode('ascii'))
                text_area.see('end')
                print(chunk.decode('ascii'))
            elif('download:' in chunk.decode()):
                get_file_name = chunk.decode().split(':')
                file_to_download = get_file_name[1]
            else:
                text_area.insert(END,"\n"+chunk.decode('ascii'))
                text_area.see("end")
                print(chunk.decode('ascii'))
        except:
            pass

def connect_to_server():
    global SERVER
    global name
    global sending_file

    cName = name.get()
    SERVER.send(cName.encode())

def connect_with_client():
    global SERVER
    global list_box

    text = list_box.get(ANCHOR)
    list_item = text.split(':')
    msg = 'connect '+list_item[1]
    SERVER.send(msg.encode('ascii'))

def disconnect_with_client():
    global SERVER
    global list_box

    text = list_box.get(ANCHOR)
    list_item = text.split(':')
    msg = 'disconnect '+list_item[1]
    SERVER.send(msg.encode('ascii'))


def showClientsList():
    global list_box

    list_box.delete(0,'end')
    SERVER.send('show list'.encode('ascii'))

def getFileSize(fileName):
    with open(fileName,'rb')as file:
        chunk = file.read()
        return len(chunk)

def sendMessage():
    global SERVER
    global text_area
    global text_message

    message = text_message.get()
    SERVER.send(message.enocde('ascii'))
    text_area.insert(END,'\n'+'You>'+message)
    text_area.see('end')
    text_message.delete(0,'end')

    if (message == 'y' or message == 'Y'):
        text_area.insert(END,'\n'+'\nPlease wait while the file downloading')
        text_area.see('end')
        HOST_NAME = '127.0.0.1'
        USER_NAME = 'lftpd'
        PASSWORD = 'lftpd'
        home = str(Path.home())
        download_path = home+'/Downloads'
        ftp_server = ftplib.FTP(HOST_NAME,USER_NAME,PASSWORD)
        ftp_server.encoding = 'utf-8'
        ftp_server.cwd('shared_files')
        fName = file_to_download
        local_file_name = os.path.join(download_path,fName)
        file = open(local_file_name,'wb')
        ftp_server.retrbinary('RETR '+fName,file.write)
        ftp_server.dir()
        file.close()
        ftp_server.quit()
        print('the file has been successfully downloaded to path'+download_path)
        text_area.insert(END,'\n'+'file has been succesfully downloaded to path'+download_path)
        text_area.see('end') 


def browseFiles():
    global text_area
    global filePathLabel
    global sending_file
    try:
        fileName = filedialog.askopenfilename()
        filePathLabel.configure(text = fileName)
        HOSTNAME = '127.0.0.1'
        USERNAME = 'lftpd'
        PASSWORD = 'lftpd'
        ftp_server = FTP(HOSTNAME,USERNAME,PASSWORD)
        ftp_server.encoding('utf-8')
        ftp_server.cwd('shared_files')
        fName = ntpath.basename(fileName)
        with open(fileName,'rb')as file:
            ftp_server.storbinary(f'STOR{fName}',file)
        
        ftp_server.dir()
        ftp_server.quit()
        message = ('send'+fName)

        if(message[:4] == 'send'):
            print('please wait')
            text_area.insert(END,'\n'+'\n please wait\n')
            text_area.see('end')
            sending_file = message[5:]
            file_size = getFileSize('shared_files/'+sending_file)
            final_message = message+' '+str(file_size)
            SERVER.send(final_message.encode())
            text_area.insert(END,'file successfully sent')
    except FileNotFoundError :
        print('cancel button pressed')


def setup():
    global SERVER
    global IP_ADDRESS
    global PORT

    SERVER = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    SERVER.connect((IP_ADDRESS,PORT))

    receive_thread = Thread(target = receive_message)
    receive_thread.start()

    open_chat_window()

setup()