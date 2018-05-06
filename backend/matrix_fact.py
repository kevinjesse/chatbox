from scipy.sparse import csr_matrix
from scipy.io import mmwrite, mmread
import database_connect
import numpy as np
import decimal
import array as arr
import pickle
import matlab.engine
import moviedb
import matlab
from typing import List

try:
    with open("netflix/movielist.txt", "rb") as fp:  # Unpickling
        movielist = pickle.load(fp)
except IOError as e:
    exit()

np.set_printoptions(threshold='nan')
eng = matlab.engine.start_matlab()
eng.cd(r'dirtyIMC_code_online')
N = mmread("./dirtyIMC_code_online/sparseN.mm.mtx")
rec_list = []
rec_values = []
X = []
U = []
V = []
# M = np.array(mmread("./dirtyIMC_code/Mgenre.mm.mtx"))
# Y = mmread("./dirtyIMC_code/sparseYgenre.mm.mtx").todense()
# M = mmread("./dirtyIMC_code/M.mm.mtx").todense()
# X = mmread("./dirtyIMC_code/XR.mm.mtx").todense()

cur = database_connect.db_connect()


def translate_dialogue(mode, movie_preferences):
    modes = ["genre", "actor", "director", "mpaa"]
    mymode = []

    if mode not in modes and mode != "all":
        print("Please specify mode: genre, actor, director, mpaa, or all")
        exit(1)

    if mode == "all":
        mymode.extend(modes)
    else:
        mymode = [mode]

    user_list = []
    mode_list = []
    if mode == "genre":
        sql_string = "SELECT genre FROM tmd_genres ORDER BY genre ASC"
        cur.execute(sql_string)
        rows = cur.fetchall()
        mode_list = [row[0] for row in rows]

        if not movie_preferences["genre"]:
            user_list = mode_list
        else:
            user_list += movie_preferences["genre"]

    elif mode == "actor" or mode == "director":
        with open("fullnameList2", "rb") as f:  # Unpickling
            mode_list = pickle.load(f)
            user_list += movie_preferences["actor"] + movie_preferences["director"]
            if not user_list:
                user_list = mode_list
    elif mode == "mpaa":
        sql_string = "SELECT DISTINCT mpaa from title"
        cur.execute(sql_string)
        rows = cur.fetchall()
        mode_list = [row[0] for row in rows]
        if not movie_preferences["mpaa"]:
            user_list = mode_list
        else:
            user_list += movie_preferences["mpaa"]
    else:
        exit(1)
    print(user_list)

    # cur.execute(sql_string)
    # rows = cur.fetchall()
    # mode_list = [row[0] for row in rows]
    # npgen = np.zeros(len(mode_list))
    # print("this is user_list")

    npgen = [0] * len(mode_list)
    if user_list:
        # print("this is user_list")
        # print(user_list)
        for item in user_list:
            # print(item)
            try:
                # npgen[mode_list.index(item)] = 1.0/(len(user_list)*3) # for all 3
                npgen[mode_list.index(item)] = 1.0 / (len(user_list))  # just genre
            except Exception as e:
                print(e)
                continue

    # return npgen.T
    return npgen

    # npgen = np.zeros((len(userlist), len(modelist)))


# matlabdata = matlab.double(X)

def train():
    M, XR, YR = eng.train2(nargout=3)
    return M, XR, YR


def test(X):
    print(X)
    value, rank = eng.test2(matlab.double(X), nargout=2)
    return rank, value


def compute_row(movie_preferences):
    global X
    XG = translate_dialogue("genre", movie_preferences)
    # XA = translate_dialogue("actor", movie_preferences)
    # XM = translate_dialogue("mpaa", movie_preferences)
    X = XG
    return test(XG)


def recommend(movie_preferences):
    global rec_list, rec_values
    rank, value = compute_row(movie_preferences)
    rec_list = list(map(int, rank[0]))
    rec_values = list(map(int, value[0]))
    # Z = compute_row(movie_preferences)[0]
    # Z[:] = [int((np.int_(x))) - 1 for x in Z] #make 0 indexed
    # Z[:] = [x - 1 for x in Z]  # make 0 indexed
    return rec_list


def online_recommend():
    global X, U, V, rec_values, rec_list
    # print rec_values
    rec_values, rec_list, U, V = eng.online_train(matlab.double(rec_values), matlab.double(U),
                                                  matlab.double(V), matlab.double(X), nargout=4)

    rec_list = list(map(int, rec_list[0]))
    rec_values = list(map(float, rec_values[0]))
    # U = map(int, reclist[0])
    # V = map(float, rec_values[0])

    print(rec_list[0:10])
    print(rec_values[0:10])

    return rec_list


def dislike(index):
    global rec_values
    for each in index:
        rec_values[each - 1] = -100
        rec_list.pop()


def like(index):
    global rec_values
    for each in index:
        rec_values[each - 1] = 1
        rec_list.pop()


def recommendation_text(i):
    output = []
    global rec_list
    tconst = None
    print(i)
    for ind in range(i, len(rec_list)):
        i = ind
        id = rec_list[ind]
        print(id)
        print(movielist[id])
        sql_string = "SELECT tconst FROM title WHERE netflixid ='{}'".format(str(movielist[int(id) - 1]))
        print(sql_string)
        cur.execute(sql_string)
        rows = cur.fetchone()
        if rows:
            print("GOT A MOVIE, BREAKING")
            print(rec_list[ind])
            tconst = rows[0]
            break

    return tconst, i

    # data = moviedb.movie_by_id(tconst)
    # # process directors and actors into readable for output
    # output.append("How about " + data[1] + " (" + data[
    #     3] + ")? ")
    # space = ""
    # rating = ""
    # if len(data) > 10:
    #     dlist = data[12].split(' ')
    #     alist = data[14].split(' ')
    #     if not data[6]:
    #         space = " not"
    #         rating = "yet"
    #     else:
    #         rating = data[6]
    #     actorNameList = moviedb.actors_by_id(alist)
    #     directorNameList = moviedb.actors_by_id(dlist)
    #     output.append(data[1] + " stars " + ", ".join(actorNameList) + " and is directed by " + \
    #                   ", ".join(directorNameList) + ".")
    # output.append("This film is {} minutes long. It is {} {} movie, and is{} rated {}.".format(
    #     data[8],
    #     "an" if any(v in data[4][:1].lower() for v in ['a', 'e', 'i', 'o', 'u']) else "a",
    #     data[4].replace(" ", ",", data[4].count(" ") - 1) \
    #         .replace(" ", " and ") \
    #         .replace(",", ", "),
    #     space,
    #     rating
    # ))
    # return output, i


def add_user(X):
    global N
    tempN = N.toarray()
    print(type(tempN))
    print(type(X))


if '__name__' == '__main__':
    userCache = {
        'mpaa': [], 'satisfied': u'NoPreference', 'actor': [], 'director': [], 'person': [], 'genre': ['comedy', ]
    }
    t = recommend(userCache)
    print(t[:2])
    dislike(t[:1])
    t = online_recommend()
    dislike(t[:1])
    t = online_recommend()
    dislike(t[:1])
    t = online_recommend()
    dislike(t[:1])
    t = online_recommend()
    dislike(t[:1])
    t = online_recommend()
    dislike(t[:1])
    # t = online_recommend()
    # dislike(t[:1])
    # t = online_recommend()
    # dislike(t[:1])
    # t = online_recommend()
    # dislike(t[:1])
    # t = online_recommend()

    # dislike(t[:10])
    # online_recommend()
    # dislike(t[:10])
    # online_recommend()
    # dislike(t[:10])
    # online_recommend()
    # dislike(t[:10])
    # online_recommend()
    # dislike(t[:10])
    # online_recommend()
    # print recommendation_text(t[0])

    # #print movie_list[20]
    #
    # II = [ 0.0,   0.0,   0.0,   0.0,   1.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,
    # 0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,   0.0,   0.0,   0.0, ]
    # # print test(II)
    # print recommend(userCache)
    # add_user(II)
