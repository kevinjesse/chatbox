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

# This api_key will be moved to a database after initial build
api_key = '166c772e6b94241f893e94b22f874c02'


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


def actorsbyID(alist):
    actornamelist = []
    for actor in alist:
        sqlstring = """SELECT primaryname FROM name WHERE nconst='""" + actor + """' LIMIT 1"""
        cur.execute(sqlstring)
        rows = cur.fetchall()
        actornamelist.append(rows[0][0])
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
