#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

from operator import itemgetter
import re

import random
import control
import responseCtrl
import database_connect
# import imdb
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

# UNABLE TO USE BECAUSE OF RECOMMENDATION SESSION authentication protocol requires
# User login. No workaround for now
def storeMovieRec(movieID):
    url = "https://api.themoviedb.org/3/account/%7Baccount_id%7D/favorite"
    payload = "{\"media_type\":\"movie\",\"media_id\":"+ movieID +",\"favorite\":true}"
    headers = {'content-type': 'application/json;charset=utf-8'}
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

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

def movieStrat(input, strategies, cache_results, curr_movie, qLib, model, resource, database, history, tfidfmodel,
               tfidfdict):
    """
    :param userid: userid generated from chatbox.php
    :param input: user text input
    :param strategies: what strategy the application is on (what task is being accomplished)
    :param cache_results: results of previous database query used for follow up requests
    :param qLib: question library
    :param model: word to vec (not used for now)
    :param resource: language resource
    :param database: (not used for now)
    :param history: user and AI response history used to know what the previous question was
    :param tfidfmodel: tf-idf model
    :param tfidfdict: tf-idf dict
    :return: text output, next question, strategies (updated), cache results (updated)
    """
    output = ''
    movies = ''
    qtup = None
    # score input
    # meta_info = control.ScoreInput(model, database, resource, input, history, tfidfmodel, tfidfdict)
    # print meta_info
    # fetch all movie data possible on highest ranked utterances
    prev_qtup = history[-1]


    if prev_qtup[1] == "m1":
        if responseCtrl.responseBinSim(input):
            output += "Ok! "
            qtup = random.choice(filter(lambda x: x[1] == 'm7', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            output += "Ok. "
            qtup = random.choice(filter(lambda x: x[1] == 'm2', qLib[strategies[-1]]))
            output += qtup[0]
            cache_results = nowPlayingMovies()
    elif prev_qtup[1] == "m2" or prev_qtup[1] == "m9":
        if responseCtrl.responseBinSim(input):
            if not cache_results:
                output += "Sorry no more films! "
                qtup = random.choice(filter(lambda x: x[1] == 'm3', qLib[strategies[-1]]))
                output += qtup[0]
            else:
                output += "Here is what I found for films now playing. "
                output += cache_results[0][1] + " (" + cache_results[0][3] + ") is " + cache_results[0][8] + " minutes and is a " + \
                              cache_results[0][4].replace(' ', ', ') + " film. Produced by " + cache_results[0][7] + ", this film's rating is " + cache_results[0][6] + ". "
                curr_movie = cache_results.pop(0)
                qtup = random.choice(filter(lambda x: x[1] == 'm8', qLib[strategies[-1]]))
                output += qtup[0]

        else:
            output += "Ok. "
            qtup = random.choice(filter(lambda x: x[1] == 'm4', qLib[strategies[-1]]))
            output += qtup[0]

    elif prev_qtup[1] == "m3" or prev_qtup[1] == "m10":
        if responseCtrl.responseBinSim(input):
            output += "Here is what I found for upcoming films. "
            #cache_results = nowPlayingMovies()
            # output += cache_results[0][1] + " (" + cache_results[0][3] + ") is " + cache_results[0][8] + " minutes and is a " + \
            #               cache_results[0][4].replace(' ', ', ') + " film. Produced by " + cache_results[0][7] + ", this film is rated " + cache_results[0][6] + ". "
            # curr_movie = cache_results.pop(0)
            qtup = random.choice(filter(lambda x: x[1] == 'm8', qLib[strategies[-1]]))
            output += qtup[0]

        else:
            output += "Ok. "
            qtup = random.choice(filter(lambda x: x[1] == 'm4', qLib[strategies[-1]]))
            output += qtup[0]

    elif prev_qtup[1] == "m6":
        # prev3_qtup = history[-5]
        #
        # #Show reviews
        # if prev3_qtup == "2":

        if responseCtrl.responseBinSim(input):
            output += "Great this movie looks good for me too. KNOW WHAT TO DO FROM DOUBLE HISTORY" \
                      "CAN EITHER show reviews or TELL YOU WHEN IT WILL BE RELEASED, TICKETS, etc"
            qtup = random.choice(filter(lambda x: x[1] == 'm6', qLib[strategies[-1]]))
            output += qtup[0]

        else:
            output += "NO! EITHER DO CACHE AGAIN with m9 or 10 Look up double history"
            qtup = random.choice(filter(lambda x: x[1] == 'm9', qLib[strategies[-1]]))
            output += qtup[0]

    elif prev_qtup[1] == "m8":
        if responseCtrl.responseBinSim(input):
            output += "I'm very good at this! "

            if prev2_qtup[1] == "m9" or prev2_qtup[1] == "m2":
                qtup = random.choice(filter(lambda x: x[1] == 'm6', qLib[strategies[-1]]))
                output += qtup[0]
            if prev2_qtup[1] == "m10" or prev2_qtup[1] == "m3":
                output += "show times are not implemented yet..."
                qtup = random.choice(filter(lambda x: x[1] == 'm5', qLib[strategies[-1]]))
                output += qtup[0]


        else:
            prev2_qtup = history[-3]
            output += "Ok. "
            if prev2_qtup[1] == "m9" or prev2_qtup[1] == "m2":
                qtup = random.choice(filter(lambda x: x[1] == 'm9', qLib[strategies[-1]]))
                output += qtup[0]
            if prev2_qtup[1] == "m10" or prev2_qtup[1] == "m3":
                qtup = random.choice(filter(lambda x: x[1] == 'm10', qLib[strategies[-1]]))
                output += qtup[0]



                    # output += "I found " + random.choice(cache_results[0])[1] + " from the genre you specified. "
        # qtup = random.choice(filter(lambda x: x[1] == 'g2', qLib[strategies[userid][-1]]))
        # output += qtup[0]
    # elif prev_qtup[1] == "m2":
    #     # Here you would do a movie lookup by the user text scored
    #     print cache_results
    #
    #     if responseCtrl.responseBinSim(input):
    #         output += "Great! "
    #         qtup = random.choice(filter(lambda x: x[1] == 'g6', qLib[strategies[-1]]))
    #         output += qtup[0]
    #     else:
    #         output += "That is too bad. "
    #         qtup = random.choice(filter(lambda x: x[1] == 'g3', qLib[strategies[-1]]))
    #         output += qtup[0]

    return output, qtup, strategies, cache_results, curr_movie
