


from scipy.sparse import csr_matrix
from scipy.io import mmwrite, mmread
import database_connect
import numpy as np
np.set_printoptions(threshold='nan')
import array as arr
import pickle
import matlab.engine
import movieCtrl
eng = matlab.engine.start_matlab()
eng.cd(r'dirtyIMC_code')
M = np.array(mmread("./dirtyIMC_code/Mgenre.mm.mtx"))
Y = mmread("./dirtyIMC_code/sparseYgenre.mm.mtx").todense()
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
        # cur.execute(sqlstring)
        # rows = cur.fetchall()
        # modelist = [row[0] for row in rows]
    elif mode == "actor" or mode == "director":
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
    npgen = np.zeros(len(modelist))
    for item in userCache[mode] :
        npgen[modelist.index(item)] = 1
    return npgen.T

    #npgen = np.zeros((len(userlist), len(modelist)))

import matlab




# Obs = mmread("./dirtyIMC_code/sparseN.mm.mtx")
# matlabdata = matlab.double(X)

def train():
    M, t = eng.train(nargout=2)
    return M

def computeRow(userCache):
    X = translateDialogue("genre", userCache)
    Z = np.matmul(X, np.matmul(M, Y.T))
    return Z

def recommend(userCache):
    Z = computeRow(userCache)
    Z = Z.tolist()
    bestScore = max(Z[0])
    RecList = [movielist[i] for i,j in enumerate(Z[0]) if j == bestScore] #netflix ids of recommendations
    if len(RecList) > 1: return RecList, recommendationText(pickTie(RecList))
    return RecList, recommendationText(RecList[1])
# Convert to names

def pickTie(RecList):
    reclistval = ["('"+str(RecList[i])+"' ," + str(i+1) + ")" for i in range(0, len(RecList))]
    idstring = """, """.join(reclistval)
    sqlstring = """SELECT title.netflixid FROM title join ratings ON title.tconst = ratings.tconst WHERE netflixid ='""" +str(RecList[0]) + """'"""
    for id in RecList[1:]:
        sqlstring += """OR netflixid='""" + str(id) + """' """
    sqlstring += """ORDER BY numvotes DESC"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    return rows[0][0]

   # # sqlstring = """SELECT tconst FROM title INNER JOIN ratings ON title.tconst=ratings.tconst WHERE """
   #  for id in RecList:
   #      sqlstring += """netflixid ='""" + str(id) + """' OR"""

def recommendationText(id):
    sqlstring = """SELECT tconst FROM title WHERE netflixid ='"""+str(id)+"""'"""
    cur.execute(sqlstring)
    rows = cur.fetchone()
    tconst = rows[0]
    data = movieCtrl.moviebyID(tconst)
    print data
    # process directors and actors into readable for output
    output = []
    output.append("How about " + data[1] + " (" + data[3] + ")? ")
    if len(data) > 10:
        dlist = data[11].split(' ')
        alist = data[14].split(' ')
        actorNameList = movieCtrl.actorsbyID(alist)
        directorNameList = movieCtrl.actorsbyID(dlist)
        output.append(data[1] + " stars " + ", ".join(actorNameList[:3]) + " and is directed by " + \
                      directorNameList[0] + ".")
    output.append("This film is " + data[8] + " minutes is a " + \
                  data[4].replace(' ', ', ') + " and is rated " + data[
                      6] +".")

    print output
    return output
# userCache = {'rating': None, 'mpaa': None, 'duration': None, 'person': None, 'year': None, 'genre': [u'comedy']}
# recommend(userCache)