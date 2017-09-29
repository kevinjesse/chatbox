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
        try:
            data = movieCtrl.moviebyID(movieWithScore[0][0])
        except Exception as e:
            print e
        output+= "From our conversation, I can recommend the following film. " + data[1] + " (" + data[
            3] + ") is " + data[8] + " minutes and is a " + \
                data[4].replace(' ', ', ') + " film. Produced by " + data[
                    7] + ", this film's rating is " + data[
                    6] + ". "

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