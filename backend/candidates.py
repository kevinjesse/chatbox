#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Candidates creates the scoring metrics and evaluates each features. This means normalizing and providing a correct score
for each row (movie)
"""

import database_connect
cur = database_connect.db_connect()

import numpy as np
np.set_printoptions(threshold='nan')

a = None
def init(tconst):
    map_array= []
    n = 0
    # sqlstring = """SELECT tconst FROM title"""
    # cur.execute(sqlstring)
    # rows = cur.fetchall()
    # for each in rows:
    #     map_array.append(each[0])
    #     n+=1

    s = (len(tconst), 5)
    return np.zeros(s), tconst

def gscore(mscores, mmap, genres):
    if genres is not None:
        total = len(genres)
        for genre in genres:
            sqlstring = """SELECT tconst FROM title WHERE genres LIKE '%""" + genre + """%'"""
            cur.execute(sqlstring)
            rows = cur.fetchall()
            for tconst in rows:
                try:
                    mscores[mmap.index(tconst[0])][0] += 1.0/total
                except ValueError:
                    continue
    return mscores

def mpaascore(mscores, mmap, mpaa):
    if mpaa is not None:
        sqlstring = """SELECT tconst FROM title WHERE mpaa ='""" + mpaa[0] +"""'"""
        for each in mpaa[1:]:
            sqlstring += """OR mpaa='""" + each + """'"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        for tconst in rows:
            try:
                mscores[mmap.index(tconst[0])][1] = 1
            except ValueError:
                continue
    return mscores

def ratingsscore(mscores, mmap) :
    sqlstring = """SELECT title.tconst, averagerating FROM title INNER JOIN ratings ON title.tconst = ratings.tconst"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for row in rows:
        try:
            mscores[mmap.index(row[0])][2] = row[1] / 10
        except ValueError:
            continue
        #-1 / (x / 5 - 2.1)
        #mscores[mmap.index(row[0])][2] = -1/(float(row[1])/5.0-2.1)*.1
    return mscores

def actorscore(mscores, mmap, people):
    if people is not None:
        for actor in people:
            sqlstring = """SELECT nconst FROM name WHERE primaryname ='"""+ actor + """' LIMIT 1"""
            cur.execute(sqlstring)
            row = cur.fetchall()
            if row:
                nconst = row[0][0]
                sqlstring = """SELECT tconst, principalcast FROM stars WHERE principalcast LIKE '%""" + nconst + """%'"""
                cur.execute(sqlstring)
                rows = cur.fetchall()
                #iterate through rows scoring the position of the actor in principal cast and
                #storing in the mscores of tconst
                for moviestartup in rows:
                    #get nconst position
                    # print moviestartup[1]
                    starlist = moviestartup[1].split(" ")
                    starlist.reverse()
                    pos = starlist.index(nconst)
                    # print nconst
                    # print starlist
                    # print pos+1
                    #print moviestartup[0]
                    try:
                        mscores[mmap.index(moviestartup[0])][3] = (pos+1)*1.0/len(starlist)
                    except ValueError:
                        continue
    return mscores

def directorscore(mscores, mmap, people):
    if people is not None:
        for director in people:
            sqlstring = """SELECT nconst FROM name WHERE primaryname ='"""+ director + """' LIMIT 1"""
            cur.execute(sqlstring)
            row = cur.fetchall()
            if row:
                nconst = row[0][0]
                sqlstring = """SELECT tconst, directors FROM crew WHERE directors LIKE '%""" + nconst + """%'"""
                cur.execute(sqlstring)
                rows = cur.fetchall()
                for moviedirtup in rows:
                    dirlist = moviedirtup[1].split(" ")
                    dirlist.reverse()
                    pos = dirlist.index(nconst)
                    try:
                        mscores[mmap.index(moviedirtup[0])][4] = (pos+1)*1.0/len(dirlist)
                    except ValueError:
                        continue
    return mscores

def find (tconst, user_pref):
    mscores, mmap = init(tconst)
    mscores = gscore(mscores, mmap, user_pref['genre'])
    mscores = mpaascore(mscores, mmap, user_pref['mpaa'])
    mscores = ratingsscore(mscores, mmap)
    mscores = actorscore(mscores, mmap, user_pref['person'])
    mscores = directorscore(mscores, mmap, user_pref['person'])
    print "candidates::mmap count: {}".format(len(mmap))
    print "candidates::mscores count: {}".format(len(mscores))

    return mscores, mmap


# import database_connect
# cur = database_connect.db_connect()
#
# import numpy as np
# np.set_printoptions(threshold='nan')
#
# a = None
# def init():
#     map_array= []
#     n = 0
#     sqlstring = """SELECT tconst FROM title"""
#     cur.execute(sqlstring)
#     rows = cur.fetchall()
#     for each in rows:
#         map_array.append(each[0])
#         n+=1
#
#     s = (n, 5)
#     return np.zeros(s), map_array
#
# def gscore(mscores, mmap, genres):
#     if genres is not None:
#         total = len(genres)
#         for genre in genres:
#             sqlstring = """SELECT tconst FROM title WHERE genres LIKE '%""" + genre + """%'"""
#             cur.execute(sqlstring)
#             rows = cur.fetchall()
#             for tconst in rows:
#                 try:
#                     mscores[mmap.index(tconst[0])][0] += 1.0/total
#                 except ValueError:
#                     continue
#     return mscores
#
# def mpaascore(mscores, mmap, mpaa):
#     if mpaa is not None:
#         sqlstring = """SELECT tconst FROM title WHERE mpaa ='""" + mpaa[0] +"""'"""
#         for each in mpaa[1:]:
#             sqlstring += """OR mpaa='""" + each + """'"""
#         cur.execute(sqlstring)
#         rows = cur.fetchall()
#         for tconst in rows:
#             mscores[mmap.index(tconst[0])][1] = 1
#     return mscores
#
# def ratingsscore(mscores, mmap) :
#     sqlstring = """SELECT title.tconst, averagerating FROM title INNER JOIN ratings ON title.tconst = ratings.tconst"""
#     cur.execute(sqlstring)
#     rows = cur.fetchall()
#     for row in rows:
#         try:
#             mscores[mmap.index(row[0])][2] = row[1] / 10
#         except ValueError:
#             continue
#         #-1 / (x / 5 - 2.1)
#         #mscores[mmap.index(row[0])][2] = -1/(float(row[1])/5.0-2.1)*.1
#     return mscores
#
# def actorscore(mscores, mmap, people):
#     if people is not None:
#         for actor in people:
#             sqlstring = """SELECT nconst FROM name WHERE primaryname ='"""+ actor + """' LIMIT 1"""
#             cur.execute(sqlstring)
#             row = cur.fetchall()
#             if row:
#                 nconst = row[0][0]
#                 sqlstring = """SELECT tconst, principalcast FROM stars WHERE principalcast LIKE '%""" + nconst + """%'"""
#                 cur.execute(sqlstring)
#                 rows = cur.fetchall()
#                 #iterate through rows scoring the position of the actor in principal cast and
#                 #storing in the mscores of tconst
#                 for moviestartup in rows:
#                     #get nconst position
#                     # print moviestartup[1]
#                     starlist = moviestartup[1].split(" ")
#                     starlist.reverse()
#                     pos = starlist.index(nconst)
#                     # print nconst
#                     # print starlist
#                     # print pos+1
#                     #print moviestartup[0]
#                     try:
#                         mscores[mmap.index(moviestartup[0])][3] = (pos+1)*1.0/len(starlist)
#                     except ValueError:
#                         continue
#     return mscores
#
# def directorscore(mscores, mmap, people):
#     if people is not None:
#         for director in people:
#             sqlstring = """SELECT nconst FROM name WHERE primaryname ='"""+ director + """' LIMIT 1"""
#             cur.execute(sqlstring)
#             row = cur.fetchall()
#             if row:
#                 nconst = row[0][0]
#                 sqlstring = """SELECT tconst, directors FROM crew WHERE directors LIKE '%""" + nconst + """%'"""
#                 cur.execute(sqlstring)
#                 rows = cur.fetchall()
#                 for moviedirtup in rows:
#                     dirlist = moviedirtup[1].split(" ")
#                     dirlist.reverse()
#                     pos = dirlist.index(nconst)
#                     try:
#                         mscores[mmap.index(moviedirtup[0])][4] = (pos+1)*1.0/len(dirlist)
#                     except ValueError:
#                         continue
#     return mscores

# def find (user_pref):
#     mscores, mmap = init()
#     mscores = gscore(mscores, mmap, user_pref['genre'])
#     mscores = mpaascore(mscores, mmap, user_pref['mpaa'])
#     mscores = ratingsscore(mscores, mmap)
#     mscores = actorscore(mscores, mmap, user_pref['person'])
#     mscores = directorscore(mscores, mmap, user_pref['person'])
#     print mscores
#     return mscores, mmap


    
    # to see what total score should be. principal cast has a max
    # length of 10 stars
    # m = 0
    # sqlstring = """SELECT directors FROM crew"""
    # cur.execute(sqlstring)
    # rows = cur.fetchall()
    # for each in rows:
    #     starlist = each[0].split(" ")
    #     tot = len(starlist)
    #     if tot>m:
    #         m = tot
    #
    # print m
