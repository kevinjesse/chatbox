# Kevin Jesse
# @author kevin.r.jesse@gmail.com
#
# import logging
# import sys

"""
Controls the dialogue chatbox. Dialogue control is called from server.py
"""

# Imports
import json

import numpy as np

import chatlogger
import database_connect
import filterMovies
import luisIntent
import luisQuery
import tellCtrl
import templateCtrl
import matrixFact #matix factorization and matrix tell

cur = database_connect.db_connect()

state = {}
history = {}
textHistory = {}
recommend = {}
cache_results = {}
curr_movie = {}
titles_user = {}
active = False
q_order = ['genre', 'actor', 'director', 'mpaa', 'tell']
has_recommended_movie = False
passiveResp = []
scoreweights = np.array([.1, .1, .5, .2, .1])

import pprint

pp = pprint.PrettyPrinter(depth=6)


# dialogueCtrl() controls dialogue flow with socket
def dialogueCtrl(input_json):
    """
    dialogueCtrl takes in data (User input), sends to dailogue logic, gets response, and returns response back to socket
    """
    try:
        global state, history, textHistory, data, cache_results, curr_movie, scoreweights, passiveResp
        js = json.loads(input_json)
        userid = js['id']
        text = js['text']
        mode = js['mode'] == "true"

        if mode:
            return listen(userid)

        output = ''
        question = None
        if userid not in state or text == '':
            state[userid] = ["genre", ]
            # TODO: Substitute temp replacement with actual recommendations
            replacement_genre = ["Action", "Comedy", "Sci-fi"]
            question = templateCtrl.get_sentence(state=state[userid][-1], is_dynamic=False)

            history[userid] = []
            textHistory[userid] = []
            cache_results[userid] = {'genre': None, 'person': None, 'mpaa': None, 'rating': None, 'year': None,
                                     'duration': None}
            curr_movie[userid] = None

            textHistory[userid].append(("C", question))
            history[userid].append((question, state[userid][-1]))
            return question, userid, 0

        query, intent, entity = luisQuery.ctrl(text)
        cache_results[userid], answered = luisIntent.ctrl(state[userid][-1], intent, entity, cache_results[userid])
        if not answered:
            # if do not understand utterance because intent is incorrect, try to find with entities
            passiveResp.append("I do not understand your answer. ")
            question = history[userid][-1][0]
        else:
            # will change state machine to class object
            if not q_order.index(state[userid][-1]) == len(q_order) - 1:
                newState = q_order[q_order.index(state[userid][-1]) + 1]
            else:
                newState = state[userid][-1]
            state[userid].append(newState)
            print "[DEBUG] cache_results: {}".format(curr_movie[userid])
            question = templateCtrl.get_sentence(state=newState, is_dynamic=False)

        # Append history
        history[userid].append((text, state[userid][-1]))
        history[userid].append((question, state[userid][-1]))
        passiveResp.append(question)
        resp = passiveResp.pop(0)

        textHistory[userid].append(("U", text))
        textHistory[userid].append(("C", resp))

        return resp, userid, len(passiveResp)

    except ValueError as e:
        return


def initResources():
    global titles
    titles = []

    # Load question library
    templateCtrl.init_resources()

    # Init list of candidate movies - (relatively new 9-20-17)
    sqlstring = """SELECT tconst FROM title"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        titles.append(mov[0])

    print "[OK] Initialization of resources."
    return


def listen(userid):
    while not len(passiveResp):
        continue
    resp = passiveResp.pop(0)
    textHistory[userid].append(("C", resp))
    return resp, userid, len(passiveResp)


def dialogueIdle(userid, debug=False):
    global active, passiveResp, has_recommended_movie
    if not state[userid]:
        return
    elif len(state[userid]) < 2:
        titles_user[userid] = titles
        return

    # Logic
    if state[userid][-2] == "bye":
        return
    elif state[userid][-2] == "mpaa":
        # output = "I like this movie because it has this"
        try:
            # outputlist = tellCtrl.ctrl(cache_results[userid], titles_user[userid],
            #                                  scoreweights, history[userid])
            movielist, outputlist = matrixFact.recommend(cache_results[userid])
            print outputlist
            for each in outputlist:
                passiveResp.append(each) #see if slower puts results in order pulls from listeners
            #passiveResp.extend(outputlist)
            has_recommended_movie = True
        except Exception as e:
            print e
        state[userid].append("bye")
        passiveResp.append("Please click on next and take the short survey.")
    else:
        titles_user[userid] = filterMovies.ctrl(state[userid][-1], cache_results[userid], titles_user[userid])

    if has_recommended_movie and debug and not passiveResp:
        chatlogger.logToFile(textHistory[userid], userid)
        has_recommended_movie = False


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


    # dialogueTest()