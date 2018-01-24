


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

    if mode == "genre":
        sqlstring = """SELECT genre FROM tmd_genres ORDER BY genre ASC"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        modelist = [row[0] for row in rows]
    elif mode == "actor" or mode == "director":
        with open("fullNamelist1.txt", "rb") as fp:  # Unpickling
            modelist = pickle.load(fp)

    elif mode == "mpaa":
        sqlstring = """SELECT DISTINCT mpaa from title ORDER BY mpaa ASC"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        modelist = [row[0] for row in rows]

    else:
        exit(1)


    # cur.execute(sqlstring)
    # rows = cur.fetchall()
    # modelist = [row[0] for row in rows]
    #npgen = np.zeros(len(modelist))
    npgen = [0]*len(modelist)
    for item in userCache[mode] :

        npgen[modelist.index(item)] = 1/len(userCache[mode])
    #return npgen.T
    return npgen

    #npgen = np.zeros((len(userlist), len(modelist)))







# matlabdata = matlab.double(X)

def train():
    M, XR, YR = eng.train2(nargout=3)
    return M, XR, YR

def test(X):
    SN = eng.test2(matlab.double(X),nargout=1)
    return SN

def computeRow(userCache):
    XG = translateDialogue("genre", userCache)
    XA = translateDialogue("actor", userCache)
    XM = translateDialogue("mpaa", userCache)
    print test(XG+XA[:275]+XM)
    return test(XG+XA[:275]+XM)[0]

def recommend(userCache):
    Z = map(int, computeRow(userCache))
    print Z
    #Z = computeRow(userCache)[0]
    #Z[:] = [int((np.int_(x))) - 1 for x in Z] #make 0 indexed
    Z[:] = [x - 1 for x in Z]  # make 0 indexed
    return Z

def recommendationText(ind):
    output = []
    global movielist
    id = movielist[ind]
    sqlstring = """SELECT tconst FROM title WHERE netflixid ='"""+str(id)+"""' ORDER BY tconst DESC LIMIT 1"""
    cur.execute(sqlstring)
    rows = cur.fetchone()
    tconst = rows[0]
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
    return output

def addUser(X):
    global N
    tempN = N.toarray()
    print type(tempN)
    print type(X)


# userCache = {'mpaa': [u'G'], 'satisfied': u'NoPreference', 'actor': ["Brad Pitt"], 'director': None, 'person': None,
#      'genre': [u'action',]}
# t = recommend(userCache)
# print t
# print recommendationText(t[0])




# #print movielist[20]
#
#II = [ 0.0,   0.0,   0.0,   0.0,   1.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,   0.0,   0.0,   0.0, ]
# # print test(II)
# print recommend(userCache)
#addUser(II)