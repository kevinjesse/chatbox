#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import responseCtrl
import random

def continueParse(input, strategies):
    if "genre" in input.lower():
        strategies.append("genre")
    elif "stars" in input.lower():
        strategies.append("stars")
    elif "movie" in input.lower():
        strategies.append("movies")
    elif "company" in input.lower():
        strategies.append("company")
    else:
        return None
    return strategies


def continueStrat(input, strategies, qLib, model, resource, database, history, tfidfmodel,
                  tfidfdict):
    """
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
    if prev_qtup[1] == "c0":
        strat = continueParse(input, strategies)
        if not strat:
            output = "I'm not sure what you mean by that. "
            qtup = random.choice(filter(lambda x: x[1] == 'c0', qLib[strategies[-1]]))
            output += qtup[0]
            return output, qtup, strategies
        output = "Ok let's do that! "
        strategies = strat
        print "The choice from stat"
        print strategies
        print
        qtup = random.choice(filter(lambda x: x[1] == strategies[-1][0] + "1", qLib[strategies[-1]]))
        output += qtup[0]
    elif prev_qtup[1] == "c1":
        if responseCtrl.responseBinSim(input):
            output += "Great! "
            qtup = random.choice(filter(lambda x: x[1] == 'c0', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            # THIS IS UNDEFINED and there is no transition to another state. This could be room for
            # non task expansion or just reloop back to intial state
            output += "Goodbye."

    elif prev_qtup[1] == "c2":
        if responseCtrl.responseBinSim(input):
            strategies.append("genre")
            output += "Great! "
            qtup = random.choice(filter(lambda x: x[1] == 'g1', qLib[strategies[-1]]))
            output += qtup[0]
        else:
            output += "OK. "
            qtup = random.choice(filter(lambda x: x[1] == 'c0', qLib[strategies[-1]]))
            output += qtup[0]

    return output, qtup, strategies
