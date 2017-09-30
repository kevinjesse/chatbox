#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#


# import logging
# import sys



# Imports
import pickle
import nltk
import os.path as path
import control, loader, nlg
import logging
import json
from gensim import corpora, models, similarities

import random
import numpy as np
# import imdb
# import genreCtrl
import movieCtrl
# import continueCtrl
import luisQuery
import luisIntent
import candidates
import entityDetect
import filterMovies
import tellCtrl

import database_connect
cur = database_connect.db_connect()

state = {}
history = {}
recommend = {}
cache_results = {}
curr_movie = {}
titles_user = {}
q_order = ['genre', 'actor', 'director', 'mpaa', 'tell']
# ia = imdb.IMDb()  # might need to move object inside thread method for multiple users

# Just TEMPORARY for debugging json and dictionaries
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


        global state, history, data, cache_results, curr_movie
        js = json.loads(input_json)
        userid = js['id']
        text = js['text']
        output = ''
        qtup = None
        if userid not in state:
            state[userid] = ["genre", ]
            qtup = random.choice(filter(lambda x: x[1] == 'genre', qLib[state[userid][-1]]))
            history[userid] = []
            #data[userid] = []
            cache_results[userid] = {'genre': None, 'person':None, 'mpaa': None, 'rating': None, 'year': None, 'duration': None}
            curr_movie[userid] = None
            history[userid].append(qtup)
            return qtup[0],userid

        query, intent, entity = luisQuery.ctrl(text)
        cache_results[userid], answered = luisIntent.ctrl(state[userid][-1], intent, entity, cache_results[userid])
        if not answered:
            #if do not understand utterance because intent is incorrect, try to find with entities
            #entityDetect.detect(state[userid][-1], entity)
            output = "I do not understand your answer. "
            qtup = history[userid][-1]
        else:
            #will change state machine to class object
            #titles_user[userid] = filterMovies.ctrl(state[userid][-1], cache_results[userid], titles_user[userid])
            if not q_order.index(state[userid][-1]) == len(q_order) - 1:
                newState = q_order[q_order.index(state[userid][-1])+1]
            else:
                newState = state[userid][-1]
            #newState = q_order[state[userid][-1] + 1]
            state[userid].append(newState)
            if newState is "tell":
                output, qtup, state[userid] = tellCtrl.ctrl(intent, state[userid], cache_results[userid], titles_user[userid], scoreweights, history[userid], qLib)
                if state[userid][-1] == "genre":
                    titles_user[userid] = titles
                # This is temporary for debugging ###########################
                # temp = ''
                # for k, v in cache_results[userid].iteritems():
                #     temp += k.title() + " : "
                #     if v:
                #         temp += ','.join(v).title() + " | \n "
                #     else:
                #         temp += 'No Preference' + " | \n "
                #         # qtup = ("Here is the information I have gathered in this conversation. " + temp, 'tell')
                #         #mscores, mmap = candidates.find(cache_results[userid])
                # mscores, mmap = candidates.find(titles_user[userid], cache_results[userid])
                # movieWithScore = sorted(zip(mmap, np.dot(mscores, scoreweights)), key=lambda tup: tup[1],
                #                         reverse=True)
                # data = movieCtrl.moviebyID(movieWithScore[0][0])
                # output += ("From our conversation, I can recommend the following film. " + data[1] + " (" + data[
                #     3] + ") is " + data[8] + " minutes and is a " + \
                #         data[4].replace(' ', ', ') + " film. Produced by " + data[
                #             7] + ", this film's rating is " + data[
                #             6] + ". ", "tell")
                        ################################################################
            # #Ask next question
            # elif newState is "satisfied":
            #     print intent
            #     state[userid].append("genre")
            else:
                qtup = random.choice(filter(lambda x: x[1] == str(newState), qLib[newState]))

            #print titles_user


        print '###################'
        print cache_results[userid]
        print '###################'

        # Append history
        history[userid].append((text, state[userid][-1]))
        history[userid].append(qtup)
        output += qtup[0]
        return output, userid
    else:
        user_data= {'rating': None, 'mpaa': [u'PG-13', u'R'], 'duration': None, 'person': [u'Tom Hanks'], 'year': None, 'genre': [u'comedy', u'action', u'adventure']}
        mscores, mmap = candidates.find(user_data)
        scoretotal = []
        # for mscore in mscores:
        #     print mscore
        movieWithScore = sorted(zip(mmap, np.dot(mscores, scoreweights)), key=lambda tup: tup[1], reverse=True)
        data = movieCtrl.moviebyID(movieWithScore[0][0])
        output = ''
        output += "From our conversation, I can recommend the following film. " + data[1] + " (" + data[3] + ") is " + data[8] + " minutes and is a " + \
                  data[4].replace(' ', ', ') + " film. Produced by " + data[7] + ", this film's rating is " + data[
                      6] + ". "
        #print movieWithScore[0]
        print output


    # if state[userid][-1] == "genre":
    #     output, qtup, state[userid], cache_results[userid], curr_movie[userid] = genreCtrl.genreStrat(text,
    #                                                                                                        state[
    #                                                                                                            userid],
    #                                                                                                        cache_results[
    #                                                                                                            userid],
    #                                                                                                        curr_movie[
    #                                                                                                            userid],
    #                                                                                                        qLib, model,
    #                                                                                                        resource,
    #                                                                                                        database,
    #                                                                                                        history[
    #                                                                                                            userid],
    #                                                                                                        tfidfmodel,
    #                                                                                                        tfidfdict)
    #     # print "This is your current movie: " + curr_movie[userid]
    # elif state[userid][-1] == "movies":
    #     output, qtup, state[userid], cache_results[userid], curr_movie[userid] = movieCtrl.movieStrat(text,
    #                                                                                                        state[
    #                                                                                                            userid],
    #                                                                                                        cache_results[
    #                                                                                                            userid],
    #                                                                                                        curr_movie[
    #                                                                                                            userid],
    #                                                                                                        qLib, model,
    #                                                                                                        resource,
    #                                                                                                        database,
    #                                                                                                        history[
    #                                                                                                            userid],
    #                                                                                                        tfidfmodel,
    #                                                                                                        tfidfdict)
    # elif state[userid][-1] == "continue":
    #     output, qtup, state[userid] = continueCtrl.continueStrat(text,
    #                                                                   state[
    #                                                                       userid],
    #                                                                   qLib, model,
    #                                                                   resource,
    #                                                                   database,
    #                                                                   history[
    #                                                                       userid],
    #                                                                   tfidfmodel,
    #                                                                   tfidfdict)

    # ---------------------------------------------For Later When we use dialogue JSONs----------------------------------
    # meta = control.FindCandidate(model, database, resource, text, history, tfidfmodel, tfidfdict)
    # relevance, answer = control.FindCandidate(model, database, resource, text, history[userid], tfidfmodel, tfidfdict)
    # print answer

    # Select state in conversation strategy
    # state, output = control.SelectState_rel_only(table_state_strategy, relevance, text, history[userid], TreeState,
    #                                             dictionary_value, q_table, TemplateLib, TopicLib, Template)

    # Theme not used just output from either end or continue
    # Fill template and output
    # output = nlg.FillTemplate(TemplateLib, TopicLib, Template[state['name']], answer, output)
    # ---------------------------------------------For Later When we use dialogue JSONs----------------------------------






    # HANDLE "I WOULD" or "SOUNDS GREAT"
    # token = nltk.word_tokenize(input)
    # try:
    #
    #
    #     lsi = models.LsiModel(model, tfidfdict, num_topics=2)
    #     vec_bow = dictionary.doc2bow(input.split())
    #     vec_lsi = lsi[vec_bow]
    #     print "PRINTING SIMILARITY SCORE"
    #     print(vec_lsi)
    #     # sim_scorey = model.n_similarity(token, "yes")
    #     # sim_scoren = model.n_similarity(token, "no")
    #     # print sim_scorey
    #     # print sim_scoren
    #     if sim_scorey > sim_scoren:
    #         return True
    #     else: return False
    # except:
    #     print "[ERROR] Out of vocabulary word occured"


def initResources():
    global TemplateLib, TopicLib, TreeState, Template, dictionary_value, resource, q_table, table_state_strategy, model, database, tfidfmodel, tfidfdict
    global qLib, titles
    database = {}
    resource = {}
    qLib = {}
    titles = []

    # listfile = None
    resource_root = 'resource'

    # # Templates
    # template_list = ['template/template_new.txt', 'template/template_end.txt', 'template/template_open.txt',
    #                  'template/template_expand.txt', 'template/template_init.txt', 'template/template_joke.txt',
    #                  'template/template_back.txt', 'template/template_more.txt']
    # template_list = [path.join(resource_root, name) for name in template_list]
    # topicfile = path.join(resource_root, 'topic.txt')

    # Dictionary
    dictionary_value = pickle.load(open(resource_root + '/pkl/dictionary_value.pkl'))

    # TFIDF dictionary and model
    tfidfname = resource_root + '/tfidf/tfidf_reference'
    tfidfdict = corpora.Dictionary.load(tfidfname + '.dict')
    tfidfmodel = models.tfidfmodel.TfidfModel.load(tfidfname + '.tfidf')

    # CNN Piers Morgan
    # listfile = resource_root + '/cnn_hr_v1_v2_v4.list'
    # datalist = [line.strip() for line in open(listfile)]

    # Load q_table for init, joke, more, switch, etc.
    q_table = pickle.load(open(resource_root + '/pkl/q_table.pkl'))

    # database of all input
    # database = loader.LoadDataPair(datalist)

    # stopwords and structure
    resource = loader.LoadLanguageResource()

    # Load template questions
    # TemplateLib = loader.LoadTemplate(template_list)

    # Topic List
    # TopicLib = loader.LoadTopic(topicfile)

    # TreeState:Load Tree True False to convo flow
    # Template links the template to convo flow piece
    # TreeState, Template = control.Init()

    model = models.Doc2Vec.load(resource_root + '/word2vec/word2vec_50')
    # table_state_strategy = pickle.load(open(resource_root + '/pkl/table_state_strategy.pkl'))
    # print tfidfmodel
    # print tfidfdict

    # qLib = loader.LoadQuestions(resource_root + '/template/template_questions.txt')
    qLib['genre'] = loader.LoadQuestions(resource_root + '/template/template_genre.txt')
    qLib['actor'] = loader.LoadQuestions(resource_root + '/template/template_actor.txt')
    qLib['director'] = loader.LoadQuestions(resource_root + '/template/template_director.txt')
    qLib['mpaa'] = loader.LoadQuestions(resource_root + '/template/template_mpaa.txt')
    qLib['tell'] = loader.LoadQuestions(resource_root + '/template/template_tell.txt')
    #qLib['tell'] = loader.LoadQuestions(resource_root + '/template/template_tell.txt')
    #qLib['movies'] = loader.LoadQuestions(resource_root + '/template/template_movies.txt')
    #qLib['continue'] = loader.LoadQuestions(resource_root + '/template/template_continue.txt')

    # Init list of candidate movies
    sqlstring = """SELECT tconst FROM title"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        titles.append(mov[0])

    print "[OK] Initialization of resources."

    return

def dialogueIdle(userid):

    print "in idle"
    if not state[userid]:
        return
    elif len(state[userid]) < 2:
        print state[userid]
        titles_user[userid] = titles
        return
    titles_user[userid] = filterMovies.ctrl(state[userid][-2], cache_results[userid], titles_user[userid])
    print titles_user

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