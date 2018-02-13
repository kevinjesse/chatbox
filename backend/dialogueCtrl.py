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
import Queue

import numpy as np

import chatlogger
import database_connect
import filterMovies
import luisIntent
import luisQuery
import luisVerify
import tellCtrl
import templateCtrl
from templateCtrl import State
import matrixFact

cur = database_connect.db_connect()

state = {}
history = {}
textHistory = {}
recommend = {}
cache_results = {}
curr_movie = {}
titles_user = {}
active = False
nomatch = {}
movieWithRatings = {}
q_order = ['genre', 'actor', 'director', 'mpaa', 'tell']
has_recommended_movie = False
passiveResp = {}
scoreweights = np.array([.2, .2, .2, .2, .2])

end_dialogue = "Bye! Please click the next button to proceed."
notperfect_string = "There is no exact match for what was specified, so I will do my best!"
no_recommendation = "I'm sorry but there is no recommendation that can be made with your criteria."
recIND = 0
import pprint

pp = pprint.PrettyPrinter(depth=6)


# dialogueCtrl() controls dialogue flow with socket
def dialogueCtrl(input_json):
    """
    dialogueCtrl takes in data (User input), sends to dialogue logic, gets response, and returns response back to socket
    """
    try:
        global state, history, textHistory, data, cache_results, curr_movie, scoreweights, passiveResp
        js = json.loads(input_json)
        userid = js['id']
        text = js['text']
        mode = js['mode'] == "true"

        if mode:
            signal = "listen"
            a, b, c = listen(userid)
            return a, b, c, signal

        output = ''
        question = ''
        if userid not in state or text == '':
            # If this is a new user
            state[userid] = ["genre", ]
            # TODO: Substitute temp replacement with actual recommendations
            replacement_genre = ["Action", "Comedy", "Sci-fi"]
            passiveResp[userid] = Queue.Queue()
            question = templateCtrl.get_sentence(state='intro', is_dynamic=False)
            question2 = templateCtrl.get_sentence(state=state[userid][-1], is_dynamic=False)
            print question
            passiveResp[userid].put(question)
            passiveResp[userid].put(question2)



            nomatch[userid] = False
            history[userid] = []
            textHistory[userid] = []
            movieWithRatings[userid] = []
            cache_results[userid] = {'genre': [], 'person': [], 'mpaa': [],'actor': [], 'director': []}
            curr_movie[userid] = None

            textHistory[userid].append(("C", question))
            history[userid].append((question, state[userid][-1]))
            return '', userid, 0, None

        query, intent, entity = luisQuery.ctrl(text)
        cache_results[userid], answered = luisIntent.ctrl(state[userid][-1], intent, entity, cache_results[userid])
        # cache_results[userid] = luisVerify.ctrl(cache_results[userid])
        if not answered:
            # if do not understand utterance because intent is incorrect, try to find with entities
            passiveResp[userid].put("I do not understand your answer. ")
            question = history[userid][-1][0]
        else:
            # will change state machine to class object
            if state[userid][-1] in q_order:
                if not q_order.index(state[userid][-1]) == len(q_order) - 1:
                    newState = q_order[q_order.index(state[userid][-1]) + 1]
                else:
                    newState = state[userid][-1]
                state[userid].append(newState)
                print "[DEBUG] cache_results: {}".format(curr_movie[userid])
                question = templateCtrl.get_sentence(state=newState, is_dynamic=False)
                print question
                print newState


        # Append history
        history[userid].append((text, state[userid][-1]))
        history[userid].append((question, state[userid][-1]))
        passiveResp[userid].put(question)
        resp = passiveResp[userid].get()

        textHistory[userid].append(("U", text))
        textHistory[userid].append(("C", resp))

        # check for end state of bye, if so, send an end signal
        print "dialogueCtrl::state: {}".format(state[userid][-1])
        signal = None
        # if state[userid][-1] == State.TELL:
        #     print "state is tell"
        #     signal = 'end'

        # if state[userid][-1] == State.BYE:
        #     print "state is bye"
        #     signal = 'end'

        return resp, userid, passiveResp[userid].qsize(), signal

    except ValueError as e:
        print "dialogueCtrl: {}".format(e)
        return '', userid, passiveResp[userid].qsize(), None


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
    # while not passiveResp[userid].qsize():
    #     continue
    resp = passiveResp[userid].get(True)
    print resp
    textHistory[userid].append(("C", resp))
    return resp, userid, passiveResp[userid].qsize()


def dialogueIdle(userid, debug=False):
    global active, passiveResp, has_recommended_movie, nomatch, movieWithRatings, recIND
    if not state[userid]:
        return
    elif len(state[userid]) < 2:
        titles_user[userid] = titles
        return

    print "dialogueIdle::state: {}".format(state[userid])
    # Logic
    if state[userid][-1] == State.BYE:
        chatlogger.logToFile(textHistory[userid], userid)
        return

    if state[userid][-2] == State.BYE:
        return

    # if state[userid][-1] != State.TELL2:
    #     titles_user[userid], match = filterMovies.ctrl(state[userid][-2], cache_results[userid],
    #                                                titles_user[userid])
    #     if not nomatch[userid] and not match:
    #         nomatch[userid] = True
    #         passiveResp[userid].put(notperfect_string, False)

    if state[userid][-1] == State.TELL:
        try:
            #movieWithRatings[userid] = tellCtrl.ctrl(cache_results[userid], titles_user[userid], scoreweights, history[userid])
            #movieWithRatings[userid] = tellCtrl.sortByRating(titles_user[userid])
            #outputlist = tellCtrl.toText(movieWithRatings[userid])
            movieWithRatings[userid] = matrixFact.recommend(cache_results[userid])
            print movieWithRatings[userid]
            outputlist, recIND = matrixFact.recommendationText(0)
            # print recIND
            # TODO: Workaround for the out of order bug, by making it a single json response
            # outputString = "<br><br>".join(outputlist)
            for each in outputlist:
                # print "Each: \n{}".format(each)
                passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners

        except Exception as e:
            print "Error at dialogueCtrl::164: {}".format(e)
        #chatlogger.logToFile(textHistory[userid], userid)
        state[userid].append(State.TELL1)
        question = templateCtrl.get_sentence(state=State.TELL1, is_dynamic=False)
        passiveResp[userid].put(question, False)

        #cache_results[userid]['satisfied'][-1] = None

    elif state[userid][-1] == State.TELL1:
        if cache_results[userid]['satisfied'] == 'Yes':  # if watched recommendation before
            state[userid].append(State.TELL1_5)
            question = templateCtrl.get_sentence(state=State.TELL1_5, is_dynamic=False)
            passiveResp[userid].put(question, False)
        else:
            state[userid].append(State.TELL2)
            question = templateCtrl.get_sentence(state=State.TELL2, is_dynamic=False)
            passiveResp[userid].put(question, False)

    elif state[userid][-1] == State.TELL1_5:
        if cache_results[userid]['satisfied'] == 'Yes':  # want new recommendations
            movieWithRatings[userid].pop(0)
            if not movieWithRatings[userid]:
                passiveResp[userid].put(no_recommendation)
                passiveResp[userid].put(end_dialogue)
                state[userid].append(State.BYE)
                return
            print movieWithRatings[userid]
            outputlist, recIND = matrixFact.recommendationText(recIND)
            for each in outputlist:
                # print "Each: \n{}".format(each)
                passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
            # passiveResp[userid].put(end_dialogue)
            state[userid].append(State.TELL1)
            question = templateCtrl.get_sentence(state=State.TELL1, is_dynamic=False)
            passiveResp[userid].put(question)
        else:
            passiveResp[userid].put(end_dialogue)
            state[userid].append(State.BYE)


    elif state[userid][-1] == State.TELL2:
        if cache_results[userid]['satisfied'] == 'Yes':
            passiveResp[userid].put(end_dialogue)
            state[userid].append(State.BYE)
        else:
            movieWithRatings[userid].pop(0)
            if not movieWithRatings[userid]:
                passiveResp[userid].put(no_recommendation)
                passiveResp[userid].put(end_dialogue)
                state[userid].append(State.BYE)
                return
            print movieWithRatings[userid]
            #outputlist = tellCtrl.toText(movieWithRatings[userid])
            outputlist, recIND = matrixFact.recommendationText(recIND)
            # print recIND
            for each in outputlist:
                # print "Each: \n{}".format(each)
                passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
            # passiveResp[userid].put(end_dialogue)
            state[userid].append(State.TELL1)
            question = templateCtrl.get_sentence(state=State.TELL1, is_dynamic=False)
            passiveResp[userid].put(question)

    if has_recommended_movie and debug and not passiveResp[userid]:
        # print "textHistory: {}".format(textHistory[userid])
        has_recommended_movie = False

    return


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
