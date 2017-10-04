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
        input_string = "\n".join("{}: {}".format(str(speaker), str(text)) for (speaker, text) in history)
        log_directory = "logs"
        try:
            os.mkdir(log_directory)
        except Exception:
            pass

        # Add time to file_name so that new log will be created each hour
        file_name = "output {}.log.txt".format(datetime.now().strftime("D=%Y-%m-%d H=%H"))

        with open(os.path.join(log_directory, file_name), "a+") as log_file:
            output = "User:\t{};\t\tTimestamp:\t{}".format(userid, datetime.now()) + "\n"
            output += input_string + "\n"
            log_file.write(output)
            log_file.close()
