from operator import itemgetter
import re

import random
import database_connect
import requests
from pprint import pprint
import csv
cur = database_connect.db_connect()


def fixer1():
    sqlstring = """SELECT api_key FROM api WHERE api_type='tmd'"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    # This api_key will be moved to a database after initial build
    api_key = rows[0][0]


    data = None
    sqlstring = """SELECT tconst, primarytitle FROM TITLE WHERE MPAA = ''"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for movie in rows:
        movieID = movie[0]
        print str(movie[1])
        url = 'https://api.themoviedb.org/3/movie/' + movieID + '/release_dates?api_key=' + api_key
        rd = requests.get(url)
        if rd.status_code != 200:
            break
        rd_json = rd.json()
        mpaa_rating = ''
        for each_dict in rd_json['results']:
            for k, v in each_dict.iteritems():
                if v == 'US':
                    if len(each_dict['release_dates']) > 1:
                        try:
                            mpaa_rating = each_dict['release_dates'][1]['certification']
                        except Exception:
                            continue
                    else:
                        mpaa_rating = each_dict['release_dates'][0]['certification']


        #pprint(mov_json)
        sqlstring = """UPDATE title SET mpaa = '""" + mpaa_rating + \
                    """'WHERE tconst='""" + movieID + """' RETURNING *"""
        # print sqlstring
        cur.execute(sqlstring)
        # rows = cur.fetchall()

def fixer2():
    sqlstring = """SELECT tconst, primarytitle FROM TITLE WHERE MPAA = ''"""
    cur.execute(sqlstring)
    rows = cur.fetchall()

    with open("mpaa.csv", "rb") as fp:
        mpaa = [entry for entry in csv.DictReader(fp, delimiter=',')]

    for movie in rows:
        movieid = movie[0]

        for each in mpaa:
            if movieid == each['tt']:
                mpaa_rating = each['mpaa']
                print str(movie[1]) + " : " + str(mpaa_rating)
                sqlstring = """UPDATE title SET mpaa = '""" + mpaa_rating + \
                             """'WHERE tconst='""" + movieid + """'"""
                cur.execute(sqlstring)
                #rows = cur.fetchall()


fixer2()