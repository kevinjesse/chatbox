import json
import os.path
from datetime import datetime
import threading
import time

# ChatLogger

create_json_file = True

threadLock = threading.Lock()

def logToFile(history, userid):
    thread = threading.Thread(target=__appendToLogFile, args=[history, userid])
    thread.daemon = False
    thread.run()

def __appendToLogFile(history, userid):
    with threadLock:
        # print "history log: {}".format(history);
        input_string = "\n".join("{}: {}".format(str(speaker), str(text)) for (speaker, text) in history)
        log_directory = "../logs/text_logs"
        try:
            os.mkdir(log_directory)
        except Exception:
            pass

        # Add time to file_name so that new log will be created each hour
        file_name = "output {}.log.txt".format(datetime.now().strftime("D=%Y-%m-%d H=%H"))

        with open(os.path.join(log_directory, file_name), "a+") as log_file:
            output = "User:\t{};\t\tTimestamp:\t{}".format(userid, datetime.now()) + "\n"
            output += input_string + "\n\n"
            log_file.write(output)
            log_file.close()

        if create_json_file:
            __appendToJsonFile(history, userid)


def __appendToJsonFile(history, userid):
    session = ChatSession(userid, datetime.now(), history)

    log_directory = "../logs/json_logs"
    try:
        os.mkdir(log_directory)
    except Exception:
        pass

    file_name = "{}.json".format(userid)

    with open(os.path.join(log_directory, file_name), "a+") as log_file:
        log_file.write("{}\n".format(session.json()))
        log_file.close()




# JSON Stuff

class ChatSession:
    userid = ''
    date = datetime.now()
    history = []

    def __init__(self, userid, date, history):
        self.userid = userid
        self.date = date
        self.history = self.__encode_history(history)


    def __encode_history(self, history):
        encodedHistory = []

        lastName = history[0][0]
        cResponses = []; uResponses = []
        for index, (name, response) in enumerate(history):
            if (lastName is 'U' and name is 'C'):
                encodedHistory.append({'c': cResponses, 'u': uResponses})
                cResponses = []; uResponses = []

            if name is 'C': cResponses.append(response)
            elif name is 'U': uResponses.append(response)

            if index == len(history) - 1:
                encodedHistory.append({'c': cResponses, 'u': uResponses})

            lastName = name

        return encodedHistory

    def json(self):
        return json.dumps({
                    'userid': self.userid,
                    'timestamp': str(self.date),
                    'history': self.history
                })
