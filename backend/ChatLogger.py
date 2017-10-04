import os.path
from datetime import datetime
import threading
import time

# ChatLogger

threadLock = threading.Lock()

def logToFile(history, userid):
    thread = threading.Thread(target=__appendToLogFile, args=[history, userid])
    thread.daemon = False
    thread.run()

def __appendToLogFile(history, userid):
    with threadLock:
        inputString = "\n".join("{}: {}".format(str(speaker), str(text)) for (speaker, text) in history)
        log_directory = "logs"
        try:
            os.mkdir(log_directory)
        except Exception:
            pass

        with open(os.path.join(log_directory, "output.txt"), "a+") as log_file:
            output = "User:\t{};\t\tTimestamp:\t{}".format(userid, datetime.now()) + "\n"
            output += inputString + "\n"
            log_file.write(output)
            log_file.close()
