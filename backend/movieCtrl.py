#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

from operator import itemgetter
import re

import random
import database_connect
import requests
from pprint import pprint

cur = database_connect.db_connect()

sqlstring = """SELECT api_key FROM api WHERE api_type='tmd'"""
cur.execute(sqlstring)
rows = cur.fetchall()
# This api_key will be moved to a database after initial build
api_key = rows[0][0]

#initialize smaller name list for memory constraint
# names = {}
# cur.execute("SET statement_timeout = '10s'")
# sqlstring = """SELECT nconst, primaryname FROM name LIMIT 800000"""
# cur.execute(sqlstring)
# rows = cur.fetchall()
# for name in rows:
#     names[name[0]] = name[1]

def moviebyID(movieID):
    """

    :param movieID:
    :return:
    """
    data = None
    sqlstring = """SELECT * FROM title INNER JOIN crew ON title.tconst=crew.tconst INNER JOIN stars ON title.tconst = stars.tconst WHERE mpaa IS NOT NULL AND title.tconst = '""" + movieID + """'"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    if not rows:
        url = 'https://api.themoviedb.org/3/movie/' + movieID + '?api_key=' + api_key
        r = requests.get(url)
        if r.status_code != 200:
            return None
        mov_json = r.json()
        url = 'https://api.themoviedb.org/3/movie/' + movieID + '/release_dates?api_key=' + api_key
        rd = requests.get(url)
        if rd.status_code != 200:
            return None

        rd_json = rd.json()
        mpaa_rating = ''
        for each_dict in rd_json['results']:
            for k, v in each_dict.iteritems():
                if v == 'US':
                    mpaa_rating = each_dict['release_dates'][0]['certification']
        #pprint(mov_json)
        sqlstring = """UPDATE title SET plot = '""" + mov_json['overview'].replace("'",
                                                                                   "''") + """', mpaa = '""" + mpaa_rating + \
                    """', prodco ='""" + mov_json['production_companies'][0]['name'].replace("'",
                                                                                             "''") + """' WHERE tconst='""" + movieID + """' RETURNING *"""
        # print sqlstring
        cur.execute(sqlstring)
        rows = cur.fetchall()
    return rows[0]


# def actorsbyID(alist):
#     actornamelist = []
#     for actor in alist:
#         sqlstring = """SELECT primaryname FROM name WHERE nconst='""" + actor + """' LIMIT 1"""
#         print sqlstring
#         cur.execute(sqlstring)
#         rows = cur.fetchall()
#         actornamelist.append(rows[0][0])
#     return actornamelist

def actorsbyID(alist):
    alistord = """'""" + """','""".join(alist) + """'"""
    alistval = ["('"+str(alist[i])+"' ," + str(i+1) + ")" for i in range(0, len(alist))]
    aliststr = """, """.join(alistval)
    actornamelist = []
    #sqlstring = """SELECT primaryname FROM name WHERE nconst IN(""" + aliststr + """) ORDER BY (nconst,""" + aliststr +""")"""
    #sqlstring = """SELECT primaryname FROM name WHERE nconst = ANY (VALUES """ + aliststr + """) ORDER BY (nconst,""" + alistord + """)"""
    #SELECT name.primaryname FROM name join ( VALUES 88340',9),('nm0000620',10)) as x (nconst, ordering) on name.nconst = x.nconst order by x.ordering
    sqlstring = """SELECT primaryname FROM name join (VALUES """ + aliststr + """) AS X (nconst, ordering) ON name.nconst = X.nconst ORDER BY X.ordering """
    # print
    # print sqlstring
    # print
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for person in rows:
        actornamelist.append(person[0])
    return actornamelist


def peoplebyID(alist):
    global names
    actornamelist = []
    for actor in alist:
        try:
            actornamelist.append(names[actor])
        except Exception as e:
            actornamelist.append("")
    return actornamelist

def directorsbyID(dlist):
    directornamelist = []
    for director in dlist:
        sqlstring = """SELECT primaryname FROM name WHERE nconst='""" + director + """' LIMIT 1"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        directornamelist.append(rows[0][0])
    return directornamelist

def upcomingMovies():
    """
    Return the top 5 upcoming movies
    :return:
    """

def nowPlayingMovies():
    """
    retrieve from the DB the list of now playing movies
    :return:
    """
    #JOING TABLE AND SORT BY DECREASING AND LIMIT TO MEH 10
    sqlstring = """SELECT * FROM title INNER JOIN tmd_nowplaying ON title.tconst=tmd_nowplaying.tconst ORDER BY vote_count DESC LIMIT 10"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    return rows
