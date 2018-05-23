from scipy.sparse import csr_matrix
from scipy.io import mmwrite, mmread, savemat
import database
import numpy as np
import decimal
import array as arr
import pickle
import matlab.engine
import moviedb
import matlab
from typing import List
import array

try:
    with open("netflix/movielist.txt", "rb") as fp:  # Unpickling
        movielist = pickle.load(fp, encoding='utf-8')
except IOError as e:
    exit()

np.set_printoptions(threshold='nan')
eng = None
N = None
Y = None
H_master = None
W_master = None

folderpath = "dirtyIMC_code_online"


def start_engine():
    global eng, N, Y, H_master, W_master
    eng = matlab.engine.start_matlab()
    eng.cd(r'dirtyIMC_code_online')
    N = mmread("./dirtyIMC_code_online/sparseN.mm.mtx")
    Y = mmread("./dirtyIMC_code_online/Y.mm.mtx")
    H_master = mmread("./dirtyIMC_code_online/H.mm.mtx")
    W_master = mmread("./dirtyIMC_code_online/W.mm.mtx")


def _translate_dialogue(mode, movie_preferences):
    """
    Translate matrix movie id to db movie id
    :param mode:
    :param movie_preferences:
    :return:
    """
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
        cur = database.connector()
        cur.execute(sql_string)
        rows = cur.fetchall()
        mode_list = [row[0] for row in rows]

        if not movie_preferences["genre"]:
            user_list = mode_list
        else:
            user_list += movie_preferences["genre"]

    elif mode == "actor" or mode == "director":
        with open("fullnameList2", "rb") as f:  # Unpickling
            mode_list = pickle.load(f, encoding='utf-8')
            user_list += movie_preferences["actor"] + movie_preferences["director"]
            if not user_list:
                user_list = mode_list
    elif mode == "mpaa":
        sql_string = "SELECT DISTINCT mpaa from title"
        cur = database.connector()
        cur.execute(sql_string)
        rows = cur.fetchall()
        mode_list = [row[0] for row in rows]
        if not movie_preferences["mpaa"]:
            user_list = mode_list
        else:
            user_list += movie_preferences["mpaa"]
    else:
        exit(1)
    print("Translate dialogue", user_list)

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

class MatrixFact:

    def __init__(self, user_id: str):
        self.user_id = user_id

        self.H = H_master.copy()
        self.W = W_master.copy()
        self.rec_counter = 0
        self.is_first_recommendation = True

        self.mat_movies = []
        self.mat_scores = []

    def _compute_row(self, movie_preferences):
        XG = _translate_dialogue("genre", movie_preferences)
        XA = _translate_dialogue("actor", movie_preferences)
        XM = _translate_dialogue("mpaa", movie_preferences)
        return XG, XA, XM

    def _predict(self, XG, XA, XM):
        print("predict")
        H_path = "u/H_{}.mat".format(self.user_id)
        W_path = "u/W_{}.mat".format(self.user_id)
        Y_path = "u/Y_{}.mat".format(self.user_id)

        savemat(folderpath + "/" + H_path, {'H': self.H})
        savemat(folderpath + "/" + W_path, {'W': self.W})
        savemat(folderpath + "/" + Y_path, {'Y': Y})

        score_row, movie_id = eng.predict(matlab.double(XG), matlab.double(XM), matlab.double(XA),
                                          W_path, H_path,
                                          Y_path, nargout=2)
        print("predict", len(score_row), len(movie_id))
        return movie_id, score_row

    def recommend(self, movie_preferences):
        XG, XA, XM = self._compute_row(movie_preferences)
        movie_id, score_row = self._predict(XG, XA, XM)
        self.mat_movies = list(map(int, movie_id[0]))
        self.mat_scores = list(map(int, score_row[0]))
        self.is_first_recommendation = False
        # return self.mat_movies, self.mat_scores

    def online_recommend(self, movie_preferences):
        XG, XA, XM = self._compute_row(movie_preferences)
        H_path = "u/H_{}.mat".format(self.user_id)
        W_path = "u/W_{}.mat".format(self.user_id)
        Y_path = "u/Y_{}.mat".format(self.user_id)
        # N_path = "u/N_{}.mat".format(self.user_id)

        savemat(folderpath + "/" + H_path, {'H': self.H})
        savemat(folderpath + "/" + W_path, {'W': self.W})
        savemat(folderpath + "/" + Y_path, {'Y': Y})
        # savemat(folderpath + "/" + N_path, {'R': N.T})

        print(len(self.mat_scores))

        W_arr, H_arr = eng.online_train(matlab.double(XG), matlab.double(XM), matlab.double(XA),
                                        Y_path, matlab.double(self.mat_scores),
                                        W_path, H_path, nargout=2)
        self.W = np.array(W_arr)
        self.H = np.array(H_arr)

        movie_id, score_row = self._predict(XG, XA, XM)

        self.mat_movies = list(map(int, movie_id[0]))
        self.mat_scores = list(map(float, score_row[0]))
        self.is_first_recommendation = False

        print(self.mat_movies[0:10])
        print(self.mat_scores[0:10])

        # return self.mat_movies, self.mat_scores

    def dislike(self):
        for each in self.mat_movies[:10]:
            self.mat_scores[each - 1] = -1000
            self.rec_counter += 1

    def like(self):
        for each in self.mat_movies[:10]:
            self.mat_scores[each - 1] = 1
            self.rec_counter += 1

    def get_movie(self):
        tconst = None
        for ind in range(self.rec_counter, len(self.mat_movies)):
            id = self.mat_movies[ind]
            print("mat_movies id", id)
            print("movie_list id", movielist[id])
            sql_string = "SELECT tconst FROM title WHERE netflixid = %s"
            cur = database.connector()
            cur.execute(sql_string, (movielist[id - 1], ))
            rows = cur.fetchone()
            if rows:
                print("GOT A MOVIE, BREAKING")
                print(self.mat_movies[ind])
                self.rec_counter = ind + 1
                tconst = rows[0]
                break

        return tconst


if __name__ == '__main__':
    start_engine()



# def get_H_W():
#     return H_master.copy(), W_master.copy()
#
#
# def train():
#     M, XR, YR = eng.train2(nargout=3)
#     return M, XR, YR
#
#
# def predict(XG, XA, XM, H, W):
#     # print(X)
#     # value is score_row, rank is movie_id
#     score_row, movie_id = eng.predict(matlab.double(XG), matlab.double(XM), matlab.double(XA), H, W, Y, nargout=2)
#     return movie_id, score_row
#
#
# def compute_row(movie_preferences, H, W):
#     XG = _translate_dialogue("genre", movie_preferences)
#     XA = _translate_dialogue("actor", movie_preferences)
#     XM = _translate_dialogue("mpaa", movie_preferences)
#     return predict(XG, XA, XM, H, W)
#
#
# def recommend(movie_preferences, H, W):
#
#     rank, value = compute_row(movie_preferences, H, W)
#     mat_movies = list(map(int, rank[0]))
#     mat_scores = list(map(int, value[0]))
#     # Z = compute_row(movie_preferences)[0]
#     # Z[:] = [int((np.int_(x))) - 1 for x in Z] #make 0 indexed
#     # Z[:] = [x - 1 for x in Z]  # make 0 indexed
#     return mat_movies, mat_scores


# def online_recommend(XG, XA, XM, H, W):
#     # print rec_values
#     eng.online_train(matlab.double(XG), matlab.double(XM), matlab.double(XA),
#                      matlab.double(Y), matlab.double(N), matlab.double(W), matlab.double(H))
#     rec_values, rec_list, U, V = eng.online_train(matlab.double(rec_values), matlab.double(U),
#                                                   matlab.double(V), matlab.double(X), nargout=4)
#
#     rec_list = list(map(int, rec_list[0]))
#     rec_values = list(map(float, rec_values[0]))
#     # U = map(int, rec_list[0])
#     # V = map(float, rec_values[0])
#
#     print(rec_list[0:10])
#     print(rec_values[0:10])
#
#     return rec_list


# def dislike(index):
#     global rec_values
#     for each in index:
#         rec_values[each - 1] = -100
#         rec_list.pop()
#
#
# def like(index):
#     global rec_values
#     for each in index:
#         rec_values[each - 1] = 1
#         rec_list.pop()


# def get_movie(i):
#     output = []
#     global rec_list
#     tconst = None
#     print("recommendation text", i)
#     for ind in range(i, len(rec_list)):
#         i = ind
#         id = rec_list[ind]
#         print("rec_list id", id)
#         print("movie_list id", movielist[id])
#         sql_string = "SELECT tconst FROM title WHERE netflixid = %s"
#         cur = database.connector().execute(sql_string, (movielist[int(id) - 1], ))
#         rows = cur.fetchone()
#         if rows:
#             print("GOT A MOVIE, BREAKING")
#             print(rec_list[ind])
#             tconst = rows[0]
#             break
#
#     return tconst, i

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

#
# def add_user(X):
#     global N
#     tempN = N.toarray()
#     print(type(tempN))
#     print(type(X))


# if '__name__' == '__main__':
#     userCache = {
#         'mpaa': [], 'satisfied': u'NoPreference', 'actor': [], 'director': [], 'person': [], 'genre': ['comedy', ]
#     }
#     t = recommend(userCache)
#     print(t[:2])
#     dislike(t[:1])
#     t = online_recommend()
#     dislike(t[:1])
#     t = online_recommend()
#     dislike(t[:1])
#     t = online_recommend()
#     dislike(t[:1])
#     t = online_recommend()
#     dislike(t[:1])
#     t = online_recommend()
#     dislike(t[:1])
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
    # print get_movie(t[0])

    # #print movie_list[20]
    #
    # II = [ 0.0,   0.0,   0.0,   0.0,   1.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,
    # 0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,   0.0,   0.0,   0.0, ]
    # # print predict(II)
    # print recommend(userCache)
    # add_user(II)
