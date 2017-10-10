#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import socket
import threading
from dialogueCtrl import dialogueCtrl, initResources, dialogueIdle
import json
import sys

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
                        # if data == "passive" and getActive():
                        #     response = getResponse()
                        #     client.send(response)
                        # elif data == "passive":
                        #     client.send('')
                        # else:
                        print data
                        # if data == "log":
                        #     pass

                        response, userid, passiveLen = dialogueCtrl(data)

                        #change to JSON
                        responseJson = json.dumps({'response':response, 'userid': userid, 'passiveLen': passiveLen})
                        client.send(responseJson)
                        dialogueIdle(userid, debug)
                    except Exception as e:
                        print e
                        import traceback
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
        ThreadingServer('localhost',13113).listen()
        # dpret, active = dialoguePassive()


