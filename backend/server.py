#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import json
import socket
import sys
import threading
import traceback
import time

import dialogue_manager as dCtrl
from dialogue_manager import dialogueCtrl, initResources, dialogueIdle

debug = False
passive = {}


def chatbox_socket():
    if debug:
        return 13120
    else:
        return 13113


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
            try:
                threading.Thread(target = self.listenToClient,args = (client,address)).start()
                # while True: time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                pass

    def listenToClient(self, client, address):
        size = 2048
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
                        print("data: {}".format(data))
                        # if data == "log":
                        #     pass

                        #signal = None

                        response, userid, passiveLen, signal = dialogueCtrl(data.decode())
                        # print response, userid, passiveLen, signal
                        # TODO: This is a bad idea but it works
                        if response == dCtrl.end_dialogue:
                            signal = 'end'

                        #change to JSON
                        responseJson = json.dumps({'response': response, 'userid': userid, 'signal': signal, 'passiveLen': passiveLen})
                        print(responseJson)
                        #time.sleep(1)
                        #print "I'm pushing! \n{}\n".format(responseJson)
                        client.send(responseJson.encode())
                        if signal != "listen":
                            dialogueIdle(userid, debug)

                    except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_tb(exc_traceback, limit=1)
                        traceback.print_exc()
                else:
                    raise Exception('Client disconnected')
            except:
                client.close()
                return False
            client.close()


if __name__ == "__main__":
    initResources()
    if 'debug' in sys.argv:
        debug = True
        print("Running in debug mode. (socket: {})".format(chatbox_socket()))
    while True:
        ThreadingServer('localhost',chatbox_socket()).listen()
        # dpret, active = dialoguePassive()


