
import pickle
import database_connect
cur = database_connect.db_connect()

def initSideDict():
    sideDict = dict()

    with open("userlist.txt", "rb") as fp:  # Unpickling
        users = pickle.load(fp)
    with open("movielist.txt", "rb") as fp:  # Unpickling
        movies = pickle.load(fp)


