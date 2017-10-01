#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

from operator import itemgetter
import re

import random
import control
import responseCtrl
import movieCtrl
import database_connect

cur = database_connect.db_connect()

def genre(meta_info):
    """
    :param meta_info: this contains the input scoring information
    :param cur: database connector
    :return: returning the search from the database for movies similar to the user top scored input
    """
    glist = sorted(meta_info, key=itemgetter(2), reverse=True)
    # sqlstring = """SELECT primarytitle FROM title INNER JOIN ratings ON title.tconst=ratings.tconst WHERE genres = ANY (VALUES ('Comedy'))"""
    # cur.execute(sqlstring)
    # rows = cur.fetchall()

    #sqlstring = """SELECT * FROM ratings"""
    sqlstring = """SELECT title.tconst, primarytitle FROM title INNER JOIN ratings ON title.tconst=ratings.tconst WHERE genres LIKE '%""" + glist[0][0]
    if len(glist) > 2:
        sqlstring += """%' AND genres LIKE '%""" + glist[1][0] + """%' AND genres LIKE '%""" +glist[2][0] + """%'"""
    elif len(glist) == 2:
        sqlstring += """%' AND genres LIKE '%""" + glist[1][0] + """%'"""
    else:
        sqlstring += """%'"""
    sqlstring += """ORDER BY numvotes DESC LIMIT 1000"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    return rows

def genreStrat(input, strategies, cache_results, curr_movie, qLib, model, resource, database, history, tfidfmodel, tfidfdict):
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
    qtup = None
    prev_qtup = history[-1]
    if prev_qtup[1] == "g0" or prev_qtup[1] == "g1":
        meta_info = control.ScoreInput(model, database, resource, input, history, tfidfmodel, tfidfdict)
        cache_results = genre(meta_info), meta_info
        if not cache_results[0]:
            output += "I could not find anything from the genre you specified. "
            qtup = random.choice(filter(lambda x: x[1] == 'g0', qLib[strategies[-1]]))
            output += qtup[0]
            return output, qtup, strategies, cache_results, None
        curr_movie = random.choice(cache_results[0])
        output += "I found " + curr_movie[1] + " from the genre you specified. "
        qtup = random.choice(filter(lambda x: x[1] == 'g2', qLib[strategies[-1]]))
        output += qtup[0]
    elif prev_qtup[1] == "g2":
        if responseCtrl.responseBinSim(input):
            output += "Great! "
            qtup = random.choice(filter(lambda x: x[1] == 'g6', qLib[strategies[-1]]))
            output += qtup[0]
            #movieCtrl.storeMovieRec(curr_movie)
        else:
            output += "That is too bad. "
            qtup = random.choice(filter(lambda x: x[1] == 'g3', qLib[strategies[-1]]))
            output += qtup[0]
    elif prev_qtup[1] == "g3":
        if responseCtrl.responseBinSim(input):
            cache_results[0].pop(0)
            curr_movie = random.choice(cache_results[0])
            output += "Cool! I found " + curr_movie[1] + " from the genre you specified. "
            qtup = random.choice(filter(lambda x: x[1] == 'g2', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            output += "OK. "
            qtup = random.choice(filter(lambda x: x[1] == 'g4', qLib[strategies[-1]]))
            output += qtup[0]
    elif prev_qtup[1] == "g4":
        if responseCtrl.responseBinSim(input):
            output += "Genres it is then!  "
            qtup = random.choice(filter(lambda x: x[1] == 'g1', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            output += "OK. "
            qtup = random.choice(filter(lambda x: x[1] == 'g5', qLib[strategies[-1]]))
            output += qtup[0]
    elif prev_qtup[1] == "g5":
        if responseCtrl.responseBinSim(input):
            output += "OK. "
            strategies.append("continue")
            qtup = random.choice(filter(lambda x: x[1] == 'c1', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            qtup = random.choice(filter(lambda x: x[1] == 'g1', qLib[strategies[-1]]))
            output += qtup[0]
    elif prev_qtup[1] == "g6":
        strategies.append("continue")
        if responseCtrl.responseBinSim(input):
            #print curr_movie
            data = movieCtrl.moviebyID(curr_movie[0])
            output += data[1] + " (" + data[3] + ") is " + data[8] + " minutes and is a " + \
                          data[4].replace(' ', ', ') + " film. Produced by " + data[7] + ", this film's rating is " + data[6] + ". "
            qtup = random.choice(filter(lambda x: x[1] == 'c1', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            qtup = random.choice(filter(lambda x: x[1] == 'c2', qLib[strategies[-1]]))
            output += qtup[0]
    return output, qtup, strategies, cache_results, curr_movie