import json
import pickle
import sys

import database_connect
import numpy as np
from scipy.io import mmwrite
from scipy.sparse import coo_matrix

userSideTop5 = {}

try:
    with open("userSideTop5.json", 'rb') as outfile:
        #userSideTop5 = pickle.load(outfile)
        userSideTop5 = json.load(outfile)
    with open("movieSideDict.json", 'rb') as outfile:
        movieSide = json.load(outfile)
        #movieSide = pickle.load(outfile)
    with open("netflix/userlist.txt", "rb") as fp:  # Unpickling
        userlist = pickle.load(fp)
    with open("netflix/movielist.txt", "rb") as fp:  # Unpickling
        movielist = pickle.load(fp)
except IOError as e:
    exit()

#Some capatibility issues between unicode and utf-8
# new = {k: unicode(v).encode("utf-8") for k,v in userSideTop5.iteritems()}
# with open("userSideTop5UTF.json", 'w') as outfile:
#     json.dump(new, outfile)

cur = database_connect.db_connect()

if len(sys.argv) == 0:
    print("Please specify mode: genre, actor, director, mpaa, or all")
    exit(1)

mode = str(sys.argv[1])
modes = ["genre", "actor", "director", "mpaa"]
mymode = []

if mode not in modes and mode != "all":
    print("Please specify mode: genre, actor, director, mpaa, or all")
    exit(1)


if mode == "all":
    mymode.extend(modes)
else:
    mymode = [mode]

for mode in mymode:
    if mode =="genre":
        sqlstring = """SELECT genre FROM tmd_genres ORDER BY genre ASC"""
        # cur.execute(sqlstring)
        # rows = cur.fetchall()
        # modelist = [row[0] for row in rows]
    elif mode =="actor" or mode == "director":
        sqlstring = """SELECT primaryname FROM name ORDER BY primaryname ASC"""
        # cur.execute(sqlstring)
        # row = cur.fetchall()
        # modelist = [name[0] for name in row]
    elif mode == "mpaa":
        sqlstring = """SELECT DISTINCT mpaa from title ORDER BY mpaa ASC"""
        # cur.execute(sqlstring)
        # row = cur.fetchall()
        # modelist = [name[0] for name in row]

    else:
        exit(1)

    cur.execute(sqlstring)
    rows = cur.fetchall()
    modelist = [row[0] for row in rows]
    npgen = np.zeros((len(userlist), len(modelist)))

    for user in userlist:
        userinfo = userSideTop5[user][mode]
        for item in userinfo:
            npgen[userlist.index(user)][modelist.index(item)] = 1
        print(user)
        #print psutil.virtual_memory()

    sparse = coo_matrix(npgen)
    mmwrite("sparseX"+mode+".mm", sparse)

    npgen = np.zeros((len(movielist), len(modelist)))

    for movieid in range(0,len(movielist)):
        movieinfo = movieSide[str(movieid)][mode]
        for item in movieinfo:
            print(item)
            npgen[movieid][modelist.index(item)] = 1
        print(movieid)
    sparse = coo_matrix(npgen)
    mmwrite("sparseY" + mode + ".mm", sparse)