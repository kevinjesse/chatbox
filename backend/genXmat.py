import json
import pickle
import numpy as np
from scipy.sparse import coo_matrix
from scipy.io import mmwrite, mmread
import database_connect
import sys
import actorNetflixReduce

userSideTop5 = {}

try:
    with open("userSideTop5.json", 'rb') as outfile:
        # userSideTop5 = pickle.load(outfile)
        userSideTop5 = json.load(outfile)

    with open("userSideDict.json", 'rb') as outfile:
        # userSideDict = pickle.load(outfile)
        userSideDict = json.load(outfile)
    with open("movieSideDict.json", 'rb') as outfile:
        movieSide = json.load(outfile)
        # movieSide = pickle.load(outfile)
    with open("netflix/userlist.txt", "rb") as fp:  # Unpickling
        userlist = pickle.load(fp)
    with open("netflix/movielist.txt", "rb") as fp:  # Unpickling
        movielist = pickle.load(fp)
except IOError as e:
    print "A file did not open"
    print e
    exit()

# Some capatibility issues between unicode and utf-8
# new = {k: unicode(v).encode("utf-8") for k,v in userSideTop5.iteritems()}
# with open("userSideTop5UTF.json", 'w') as outfile:
#     json.dump(new, outfile)

cur = database_connect.db_connect()

if len(sys.argv) == 0:
    print "Please specify mode: genre, actor, director, mpaa, or all"
    exit(1)

mode = str(sys.argv[1])
modes = ["genre", "actor", "director", "mpaa"]
mymode = []

if mode not in modes and mode != "all":
    print "Please specify mode: genre, actor, director, mpaa, or all"
    exit(1)

if mode == "all":
    mymode.extend(modes)
else:
    mymode = [mode]

for mode in mymode:
    if mode == "genre":
        sqlstring = """SELECT genre FROM tmd_genres ORDER BY genre ASC"""
        # cur.execute(sqlstring)
        # rows = cur.fetchall()
        # modelist = [row[0] for row in rows]
        cur.execute(sqlstring)
        rows = cur.fetchall()
        modelist = [row[0] for row in rows]
        npgen = np.zeros((len(userlist), len(modelist)))

        for user in userlist:
            if user == '1557557': continue
            totalfreq = 0
            userinfo = userSideDict[user][mode]
            for item, freq in userinfo.iteritems():
                try:
                    npgen[userlist.index(user)][modelist.index(item)] = freq
                    totalfreq += freq
                except ValueError:
                    continue

            npgen[userlist.index(user)] /= totalfreq
            print str(user) + ", total freq: " + str(totalfreq)
            #     #print psutil.virtual_memory()

            # for user in userlist:
            #     userinfo = userSideTop5[user][mode]
            #     for item in userinfo:
            #         npgen[userlist.index(user)][modelist.index(item)] = 1
            #     print user
            # print psutil.virtual_memory()

        sparse = coo_matrix(npgen)
        mmwrite("sparseX" + mode + ".mm", sparse)

        ##

        npgen = np.zeros((len(movielist), len(modelist)))

        for movieid in range(0, len(movielist)):
            movieinfo = movieSide[str(movieid)][mode]
            freq = 0
            for item in movieinfo:
                try:
                    print item

                    npgen[movieid][modelist.index(item)] = 1
                    freq += 1
                except ValueError:
                    continue
            print movieid
            print freq
            if freq != 0:
                npgen[movieid] /= freq
        sparse = coo_matrix(npgen)
        mmwrite("sparseY" + mode + ".mm", sparse)


    elif mode == "actor" or mode == "director":
        # sqlstring = """SELECT primaryname FROM name INNER JOIN tmd_popular_actors ON name.nconst = tmd_popular_actors.nconst ORDER BY tmd_popular_actors.pos ASC"""
        # cur.execute(sqlstring)
        # row = cur.fetchall()
        # modelist = [name[0] for name in row]
        tconst, modelist = actorNetflixReduce.fetch()

        npgen = np.zeros((len(userlist), len(modelist)))
        for user in userlist:
            if user == '1557557': continue
            totalfreq = 0
            userinfo = userSideDict[user][mode]
            for item, freq in userinfo.iteritems():
                # print item
                # print freq
                try:
                    npgen[userlist.index(user)][modelist.index(item)] = freq
                    totalfreq += freq
                except ValueError:
                    continue

            npgen[userlist.index(user)] /= totalfreq
            print str(user) + ", total freq: " + str(totalfreq)
            #     #print psutil.virtual_memory()

            # for user in userlist:
            #     userinfo = userSideTop5[user][mode]
            #     for item in userinfo:
            #         npgen[userlist.index(user)][modelist.index(item)] = 1
            #     print user
            # print psutil.virtual_memory()

        sparse = coo_matrix(npgen)
        mmwrite("sparseX" + mode + ".mm", sparse)

        npgen = np.zeros((len(movielist), len(modelist)))

        for movieid in range(0, len(movielist)):
            movieinfo = movieSide[str(movieid)][mode]
            freq = 0
            for item in movieinfo:
                try:
                    print item

                    npgen[movieid][modelist.index(item)] = 1
                    freq += 1
                except ValueError:
                    continue
            # print movieid
            # print freq
            if freq != 0:
                npgen[movieid] /= freq
        sparse = coo_matrix(npgen)
        mmwrite("sparseY" + mode + ".mm", sparse)


    elif mode == "mpaa":
        sqlstring = """SELECT DISTINCT mpaa FROM title"""

        cur.execute(sqlstring)
        rows = cur.fetchall()
        modelist = [row[0] for row in rows]
        npgen = np.zeros((len(userlist), len(modelist)))
        for user in userlist:
            if user == '1557557': continue
            totalfreq = 0
            userinfo = userSideDict[user][mode]
            for item, freq in userinfo.iteritems():
                # print item
                # print freq
                try:
                    npgen[userlist.index(user)][modelist.index(item)] = freq
                    totalfreq += freq
                except ValueError:
                    continue

            npgen[userlist.index(user)] /= totalfreq
            print str(user) + ", total freq: " + str(totalfreq)
            #     #print psutil.virtual_memory()

            # for user in userlist:
            #     userinfo = userSideTop5[user][mode]
            #     for item in userinfo:
            #         npgen[userlist.index(user)][modelist.index(item)] = 1
            #     print user
            # print psutil.virtual_memory()

        sparse = coo_matrix(npgen)
        mmwrite("sparseX" + mode + ".mm", sparse)

        npgen = np.zeros((len(movielist), len(modelist)))

        for movieid in range(0, len(movielist)):
            try:
                movieinfo = movieSide[str(movieid)][mode]
            except KeyError:
                continue

            freq = 0
            for item in movieinfo:
                try:
                    print item

                    npgen[movieid][modelist.index(item)] = 1
                    freq += 1
                except ValueError:
                    continue
            # print movieid
            # print freq
            if freq != 0:
                npgen[movieid] /= freq
        sparse = coo_matrix(npgen)
        mmwrite("sparseY" + mode + ".mm", sparse)

    else:
        exit(1)

        # cur.execute(sqlstring)
        # rows = cur.fetchall()
        # modelist = [row[0] for row in rows]
        # npgen = np.zeros((len(userlist), len(modelist)))


# X Matrice


