#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import socket
import threading
import dialogueCtrl as dCtrl
from dialogueCtrl import dialogueCtrl, initResources, dialogueIdle
import json
import sys
import os
import traceback
debug = False

class ThreadingServer(object):
    """
    Threading server for every interaction with backend. Creates thread on each message to allow for multiple
    messages sent before response.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        self.sock.settimeout(None)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                #print(data)
                if data:
                    # print data
                    try:
                        # Test for clicking next button on chatbox.php
                        #js = json.loads(data);
                        #if js["getJson"] == True:


                        # if data == "passive" and getActive():
                        #     response = getResponse()
                        #     client.send(response)
                        # elif data == "passive":
                        #     client.send('')
                        # else:
                        print "data: {}".format(data)
                        # if data == "log":
                        #     pass

                        #signal = None
                        response, userid, passiveLen, signal = dialogueCtrl(data)
                        print response, userid, passiveLen, signal
                        # TODO: This is a bad idea but it works
                        if response == dCtrl.end_dialogue:
                            signal = 'end'

                        #change to JSON
                        responseJson = json.dumps({'response': response, 'userid': userid, 'signal': signal, 'passiveLen': passiveLen})
                        client.send(responseJson)
                        dialogueIdle(userid, debug)

                    except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_tb(exc_traceback, limit=1,)
                        traceback.print_exc()
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    initResources()
    if 'debug' in sys.argv: debug = True
    while True:
        ThreadingServer('localhost/chatbox-base',13113).listen()
        # dpret, active = dialoguePassive()


