


from scipy.sparse import csr_matrix
from scipy.io import mmwrite, mmread
import database_connect
import numpy as np
import decimal
np.set_printoptions(threshold='nan')
import array as arr
import pickle
import matlab.engine
import movieCtrl
import matlab
eng = matlab.engine.start_matlab()
eng.cd(r'dirtyIMC_code')
N = mmread("./dirtyIMC_code/sparseN.mm.mtx")
reclist = []
# M = np.array(mmread("./dirtyIMC_code/Mgenre.mm.mtx"))
# Y = mmread("./dirtyIMC_code/sparseYgenre.mm.mtx").todense()
# M = mmread("./dirtyIMC_code/M.mm.mtx").todense()
# X = mmread("./dirtyIMC_code/XR.mm.mtx").todense()

try:
    with open("netflix/movielist.txt", "rb") as fp:  # Unpickling
        movielist = pickle.load(fp)
except IOError as e:
    exit()

import sys
cur = database_connect.db_connect()

def translateDialogue(mode,userCache):
    modes = ["genre", "actor", "director", "mpaa"]
    mymode = []

    if mode not in modes and mode != "all":
        print "Please specify mode: genre, actor, director, mpaa, or all"
        exit(1)

    if mode == "all":
        mymode.extend(modes)
    else:
        mymode = [mode]
    userlist = []
    if mode == "genre":
        sqlstring = """SELECT genre FROM tmd_genres ORDER BY genre ASC"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        modelist = [row[0] for row in rows]

        if not userCache["genre"]:
            userlist = modelist
        else:
            userlist += userCache["genre"]


        #userlist += userCache["genre"]
    elif mode == "actor" or mode == "director":
        with open("fullnameList2", "rb") as fp:  # Unpickling
            modelist = pickle.load(fp)
            userlist += userCache["actor"] + userCache["director"]
            if not userlist:
                userlist = modelist
    elif mode == "mpaa":
        sqlstring = """SELECT DISTINCT mpaa from title"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        modelist = [row[0] for row in rows]
        if not userCache["mpaa"]:
            userlist = modelist
        else:
            userlist += userCache["mpaa"]
    else:
        exit(1)
    print userlist

    # cur.execute(sqlstring)
    # rows = cur.fetchall()
    # modelist = [row[0] for row in rows]
    #npgen = np.zeros(len(modelist))
    #print "this is userlist"
    npgen = [0]*len(modelist)
    if userlist:
        # print "this is userlist"
        # print userlist
        for item in userlist :
            # print item
            try:
                npgen[modelist.index(item)] = 1.0/(len(userlist)*3)
            except Exception as e:
                print e
                continue

    #return npgen.T
    return npgen

    #npgen = np.zeros((len(userlist), len(modelist)))







# matlabdata = matlab.double(X)

def train():
    M, XR, YR = eng.train2(nargout=3)
    return M, XR, YR

def test(X):
    print X
    SN = eng.test2(matlab.double(X),nargout=1)
    return SN

def computeRow(userCache):
    XG = translateDialogue("genre", userCache)
    XA = translateDialogue("actor", userCache)
    XM = translateDialogue("mpaa", userCache)
    # print test(XG+XA[:275]+XM)
    return test(XG+XM+XA)[0]

def recommend(userCache):
    global reclist
    Z = map(int, computeRow(userCache))
    reclist = Z
    #print Z
    #Z = computeRow(userCache)[0]
    #Z[:] = [int((np.int_(x))) - 1 for x in Z] #make 0 indexed
    #Z[:] = [x - 1 for x in Z]  # make 0 indexed
    return Z

def recommendationText(i):
    output = []
    global reclist
    tconst = None
    print i
    for ind in range(i, len(reclist)):
        i = ind
        id = reclist[ind]
        print id
        print movielist[id]
        sqlstring = """SELECT tconst FROM title WHERE netflixid ='"""+str(movielist[int(id)-1])+"""'"""
        print sqlstring
        cur.execute(sqlstring)
        rows = cur.fetchone()
        if rows:
            print "GOT A MOVIE, BREAKING"
            print reclist[ind]
            tconst = rows[0]
            break



    data = movieCtrl.moviebyID(tconst)
    # process directors and actors into readable for output
    output.append("How about " + data[1] + " (" + data[
        3] + ")? ")
    space = ""
    rating = ""
    if len(data) > 10:
        dlist = data[12].split(' ')
        alist = data[14].split(' ')
        if not data[6]:
            space = " not"
            rating = "yet"
        else:
            rating = data[6]
        actorNameList = movieCtrl.actorsbyID(alist)
        directorNameList = movieCtrl.actorsbyID(dlist)
        output.append(data[1] + " stars " + ", ".join(actorNameList) + " and is directed by " + \
                      ", ".join(directorNameList) + ".")
    output.append("This film is {} minutes long. It is {} {} movie, and is{} rated {}.".format(
        data[8],
        "an" if any(v in data[4][:1].lower() for v in ['a', 'e', 'i', 'o', 'u']) else "a",
        data[4].replace(" ", ",", data[4].count(" ") - 1) \
            .replace(" ", " and ") \
            .replace(",", ", "),
        space,
        rating
    ))
    return output, i

def addUser(X):
    global N
    tempN = N.toarray()
    print type(tempN)
    print type(X)


# userCache = {'mpaa': [], 'satisfied': u'NoPreference', 'actor': [], 'director': [], 'person': [], 'genre': ['comedy',]}
# t = recommend(userCache)
# print t
# print recommendationText(t[0])




# #print movielist[20]
#
#II = [ 0.0,   0.0,   0.0,   0.0,   1.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,   0.0,   0.0,   0.0, ]
# # print test(II)
# print recommend(userCache)
#addUser(II)