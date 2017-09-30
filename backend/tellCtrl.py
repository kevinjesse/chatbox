#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import database_connect
import numpy as np
import candidates
import movieCtrl
import random
cur = database_connect.db_connect()

def ctrl(intent, state, cache_results, titles_user, scoreweights, history, qLib):
    print intent
    print state
    prev_qtup = history[-1]
    output = ''
    qtup = None
    if prev_qtup[1] == "mpaa":
        temp = ''
        for k, v in cache_results.iteritems():
            temp += k.title() + " : "
            if v:
                temp += ','.join(v).title() + " | \n "
            else:
                temp += 'No Preference' + " | \n "
                # qtup = ("Here is the information I have gathered in this conversation. " + temp, 'tell')
                # mscores, mmap = candidates.find(cache_results[userid])
        mscores, mmap = candidates.find(titles_user, cache_results)
        movieWithScore = sorted(zip(mmap, np.dot(mscores, scoreweights)), key=lambda tup: tup[1],
                                reverse=True)

        #not sure why this occasionally excepts keyerror from movieWith Score
        try:
            data = movieCtrl.moviebyID(movieWithScore[0][0])

            #process directors and actors into readable for output
            dlist = data[10].split(' ')
            alist = data[13].split(' ')
            actorNameList = movieCtrl.actorsbyID(alist)
            directorNameList = movieCtrl.directorsbyID(dlist)

            output += "How about " + data[1] + " (" + data[
                3] + ")? " + data[1] + " stars " + ", ".join(actorNameList[:3]) + "and is directed by " + \
                      directorNameList[0] + ". This film is " + data[8] + " minutes is a " + \
                      data[4].replace(' ', ', ') + " and rated " + data[
                          6] + " film."

        except Exception as e:
            print e

        # output += "How about " + data[1] + " (" + data[
        #     3] + ")? " + data[1] + " stars " + ", ".join(actorNameList[:3]) + "and is directed by " + \
        #           directorNameList[0] + ". This film is " + data[8] + " minutes is a " + \
        #           data[4].replace(' ', ', ') + " and rated " + data[
        #               6] + " film."

        qtup = random.choice(filter(lambda x: x[1] == 't0', qLib[state[-1]]))
    elif prev_qtup[1] == "t0":
        if intent['intent'] == "No":
            state.append("genre")
            qtup = random.choice(filter(lambda x: x[1] == 'genre', qLib[state[-1]]))
        elif intent['intent'] == "Yes":
            output += "Ok, Bye!"
            qtup = ("", "")

    print prev_qtup
    return output, qtup, state