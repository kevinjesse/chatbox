# Kevin Jesse
# @author kevin.r.jesse@gmail.com
#
# import logging
# import sys



# Imports
import loader
import json

import random
import numpy as np
import movieCtrl
import luisQuery
import luisIntent
import candidates
import entityDetect
import filterMovies
import tellCtrl
import ChatLogger

import database_connect
cur = database_connect.db_connect()



state = {}
history = {}
textHistory = {}
recommend = {}
cache_results = {}
curr_movie = {}
titles_user = {}
q_order = ['genre', 'actor', 'director', 'mpaa', 'tell']
hasRecommendedMovie = False


import pprint
pp = pprint.PrettyPrinter(depth=6)

# dialogueCtrl() controls dialogue flow with socket
def dialogueCtrl(input_json):
    """
    dialogueCtrl takes in data (User input), sends to dailogue logic, gets response, and returns response back to socket
    """
    scoreweights = np.array([.1, .1, .5, .2, .1])

    # Dont worry input_json can never be set to "debug" unless done in code...
    if input_json is not "debug":


        global state, history, textHistory, data, cache_results, curr_movie, hasRecommendedMovie
        js = json.loads(input_json)
        userid = js['id']
        text = js['text']
        output = ''
        qtup = None
        if userid not in state:
            # First time the user visits the page
            state[userid] = ["genre", ]
            qtup = random.choice(filter(lambda x: x[1] == 'genre', qLib[state[userid][-1]]))
            history[userid] = []
            textHistory[userid] = []
            #data[userid] = []
            cache_results[userid] = {'genre': None, 'person':None, 'mpaa': None, 'rating': None, 'year': None, 'duration': None}
            curr_movie[userid] = None
            textHistory[userid].append(("C", qtup[0]))
            history[userid].append(qtup)
            return qtup[0],userid

        query, intent, entity = luisQuery.ctrl(text)
        cache_results[userid], answered = luisIntent.ctrl(state[userid][-1], intent, entity, cache_results[userid])
        if not answered:
            #if do not understand utterance because intent is incorrect, try to find with entities
            output = "I do not understand your answer. "
            qtup = history[userid][-1]
        else:
            #will change state machine to class object
            if not q_order.index(state[userid][-1]) == len(q_order) - 1:
                newState = q_order[q_order.index(state[userid][-1])+1]
            else:
                newState = state[userid][-1]
            state[userid].append(newState)
            if newState is "tell":
                # The sentence of the movie suggestion
                # TODO: append to history (AND CHECK History tuple)
                output, qtup, state[userid] = tellCtrl.ctrl(intent, state[userid], cache_results[userid], titles_user[userid], scoreweights, history[userid], qLib)
                print "dialogueCtrl qtup @ line 90: {}".format(qtup)
                hasRecommendedMovie = True
                print "boolFlag @ 92: {}".format(hasRecommendedMovie)
                if state[userid][-1] == "genre":
                    titles_user[userid] = titles
            else:
                qtup = random.choice(filter(lambda x: x[1] == str(newState), qLib[newState]))

        # Append history
        history[userid].append((text, state[userid][-1]))
        history[userid].append(qtup)
        output += qtup[0]

        # Append to text file
        textHistory[userid].append(("U", text))
        textHistory[userid].append(("C", output))

        return output, userid
    else:

        user_data= {'rating': None, 'mpaa': [u'PG-13', u'R'], 'duration': None, 'person': [u'Tom Hanks'], 'year': None, 'genre': [u'comedy', u'action', u'adventure']}
        mscores, mmap = candidates.find(user_data)
        movieWithScore = sorted(zip(mmap, np.dot(mscores, scoreweights)), key=lambda tup: tup[1], reverse=True)
        data = movieCtrl.moviebyID(movieWithScore[0][0])
        output = ''
        output += "From our conversation, I can recommend the following film. " + data[1] + " (" + data[3] + ") is " + data[8] + " minutes and is a " + \
                  data[4].replace(' ', ', ') + " film. Produced by " + data[7] + ", this film's rating is " + data[
                      6] + ". "
        print output

def initResources():
    global qLib, titles
    qLib = {}
    titles = []

    #Load question library
    resource_root = 'resource'
    qLib['genre'] = loader.LoadQuestions(resource_root + '/template/template_genre.txt')
    qLib['actor'] = loader.LoadQuestions(resource_root + '/template/template_actor.txt')
    qLib['director'] = loader.LoadQuestions(resource_root + '/template/template_director.txt')
    qLib['mpaa'] = loader.LoadQuestions(resource_root + '/template/template_mpaa.txt')
    qLib['tell'] = loader.LoadQuestions(resource_root + '/template/template_tell.txt')

    # Init list of candidate movies - (relatively new 9-20-17)
    sqlstring = """SELECT tconst FROM title"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        titles.append(mov[0])

    print "[OK] Initialization of resources."

    return

def dialogueIdle(userid):

    if not state[userid]:
        return
    elif len(state[userid]) < 2:
        print "state[userid]: {}".format(state[userid])
        titles_user[userid] = titles
        return
    titles_user[userid] = filterMovies.ctrl(state[userid][-2], cache_results[userid], titles_user[userid])

    print "titles_user count: {}".format(len(titles_user[userid]))
    print "HasRecommendedMovie: {}".format(hasRecommendedMovie)

    #print "HEREHEREHERE"
    #print "State: {} \nCache: {} \nTitles: {}".format(state[userid][-2], cache_results[userid], titles_user[userid])

    if hasRecommendedMovie:
        ChatLogger.logToFile(textHistory[userid], userid)
    #print "HEREHEREHEREMMMMMMMMM"
    #print "State: {} \nCache: {} \nTitles: {}".format(state[userid][-2], cache_results[userid], titles_user[userid])

def dialogueTest():
    print '[OK] Start dialogue test'
    # import pprint
    # pp = pprint.PrettyPrinter(depth=6)

    initResources()
    # state["599f6b6e8a3fd"] = ["genre"]
    # history["599f6b6e8a3fd"] = []
    dialogueCtrl('debug')
    print '[OK] End dialogue test'
    return


#dialogueTest()