
import pickle
import database_connect
from movieCtrl import actorsbyID, directorsbyID
from scipy.sparse import coo_matrix
from scipy.io import mmwrite, mmread
import json

cur = database_connect.db_connect()

sidefields= ['genre', 'actor', 'director', 'mpaa']

sparse = mmread("./netflix/sparseN.mm.mtx")
users = []
movies = []

def sparse_favorite():
    mov_reduce = []
    user_reduce = []
    ratings_reduce = []
    for movie,user,rating in zip(sparse.row, sparse.col, sparse.data):
        if rating > 4:
            mov_reduce.append(movie)
            user_reduce.append(user)
            ratings_reduce.append(rating)

    sparse_favorites = coo_matrix((ratings_reduce,(mov_reduce,user_reduce)))
    return sparse_favorites


def initSideDict():
    sideDict = dict()
    global users, movies
    with open("./netflix/userlist.txt", "rb") as fp:  # Unpickling
        users = pickle.load(fp)
    with open("./netflix/movielist.txt", "rb") as fp:  # Unpickling
        movies = pickle.load(fp)

    for user in users:
        userdict = dict()
        for field in sidefields:
            userdict[field] = {}
        sideDict[user] = userdict

    return sideDict

def fillSideDict(sparse, sideDict):
    movieSideDict = {}
    lastmov= None
    for i, j, v in zip(sparse.row, sparse.col, sparse.data):
        #if i == 1: break
        #look up about movie
        #Only do if we havent seen this movie

        if i != lastmov:
            print (str(i) + ":" + str(movies[i]))
            #print (str(i) + ":" + str(movies[i]))
            netflixid = movies[i]
            ind = str(i)

            #init 5 fields
            tempdict = dict()
            for field in sidefields:
                tempdict[field] = []
            movieSideDict[ind] = tempdict

            #Get and place movie side information
            sqlstring = """SELECT * FROM title INNER JOIN STARS ON title.tconst = stars.tconst INNER JOIN crew ON title.tconst = crew.tconst WHERE netflixid='""" + netflixid +"""'"""
            cur.execute(sqlstring)
            row = cur.fetchone()
            if row:
                movieSideDict[ind]['genre'] = row[4].split(" ")
                # movieSideDict[i]['actor'] = actorsbyID(row[11].split(" "))
                movieSideDict[ind]['actor'] = row[11].split(" ")
                # movieSideDict[i]['director'] = actorsbyID(row[13].split(" "))
                movieSideDict[ind]['director'] = row[13].split(" ")
                movieSideDict[ind]['mpaa'] = row[6]


            # print genres
            # print actors
            # print directors
            #insert row values into appropriate spots
        lastmov = i
        # print sideDict
        #print movieSideDict

        for k,v in movieSideDict[ind].iteritems():
            if v:
                if k != 'mpaa':
                    for val in v:
                        try:
                            #print sideDict[users[j]][k]
                            sideDict[users[j]][k][val] += 1
                        except KeyError as e:
                            #sideDict[users[j]][k] = dict()
                            sideDict[users[j]][k][val] = 1
                else:
                    try:
                        # print sideDict[users[j]][k]
                        print k
                        print v
                        sideDict[users[j]][k][v] += 1
                    except KeyError as e:
                        # sideDict[users[j]][k] = dict()
                        sideDict[users[j]][k][v] = 1
                #sideDict[users[j]][k].extend(v)
                #NO DUP
                #make each a dictionary and only append top 5 for each category
                #sideDict[users[j]][k] = sideDict[users[j]][k] + list(set(sideDict[users[j]][k]) - set(v))

    return sideDict, movieSideDict


def fillFullSideMovieDict():
    movieSideDict = {}
    lastmov= None
    for i in range(0,len(movies)):
        #if i == 1: break
        #look up about movie
        #Only do if we havent seen this movie

        if i != lastmov:
            print (str(i) + ":" + str(movies[i]))
            netflixid = movies[i]
            ind = str(i)


            #init 5 fields
            tempdict = dict()
            for field in sidefields:
                tempdict[field] = []
            movieSideDict[ind] = tempdict

            #Get and place movie side information
            sqlstring = """SELECT * FROM title INNER JOIN STARS ON title.tconst = stars.tconst INNER JOIN crew ON title.tconst = crew.tconst WHERE netflixid='""" + netflixid +"""'"""
            cur.execute(sqlstring)
            row = cur.fetchone()
            if row:
                movieSideDict[ind ]['genre'] = row[4].split(" ")
                #movieSideDict[i]['actor'] = actorsbyID(row[11].split(" "))
                movieSideDict[ind ]['actor'] = row[11].split(" ")
                #movieSideDict[i]['director'] = actorsbyID(row[13].split(" "))
                movieSideDict[ind ]['director'] = row[13].split(" ")
                movieSideDict[ind ]['mpaa'] = [row[6]]
            #print movieSideDict[i]

            # print genres
            # print actors
            # print directors
            #insert row values into appropriate spots
        lastmov = i
    return movieSideDict

def howManyReviewsInSparse(sparse_fav):
    count = {}
    for i, j, v in zip(sparse_fav.row, sparse_fav.col, sparse_fav.data):
        try:
            count[j] += 1
        except KeyError as e:
            count[j] = 1

    smallcount = sorted(count.items(), key=lambda (k, v): v, reverse=True)
    print "SMALL"
    print smallcount[-1]
    print "BIG"
    print smallcount[0]

sparse_fav = sparse_favorite()
sideDict = initSideDict()
userSideDict, movieSideDict = fillSideDict(sparse_fav, sideDict)
with open("userSideDict.json", 'w') as outfile:
    json.dump(userSideDict, outfile)



#For full dictionary
# movieSideDict = fillFullSideMovieDict()
with open("movieSideDict.json", 'w') as f:
    json.dump(movieSideDict, f)