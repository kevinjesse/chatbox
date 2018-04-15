# Kevin Jesse
# @author kevin.r.jesse@gmail.com
#
# import logging
# import sys

"""
Controls the dialogue chatbox. Dialogue control is called from server.py
"""

import json
import queue
import numpy as np

import chatlogger
import database_connect
import filterMovies
import luisIntent
import luisQuery
import tellCtrl
import template_manager
from template_manager import State

cur = database_connect.db_connect()

# state = {}
# history = {}
# textHistory = {}
# recommend = {}
# cache_results = {}
# curr_movie = {}
# titles_user = {}
# active = False
# nomatch = {}
# movie_with_ratings = {}
# q_order = ['genre', 'actor', 'director', 'mpaa', 'tell']
# has_recommended_movie = False
# passiveResp = {}
# scoreweights = np.array([.2, .2, .2, .2, .2])


class User:

    class States:
        possible_states = [State.INTRO,
                           State.GENRE,
                           State.ACTOR,
                           State.DIRECTOR,
                           State.MPAA,
                           State.TELL,
                           State.TELL1,
                           State.TELL1_5,
                           State.TELL2,
                           State.BYE]

        def __init__(self):
            self._current_state_id = 0

        @property
        def current_state(self) -> State:
            return User.States.possible_states[self._current_state_id]

        def next(self) -> State:
            if self._current_state_id < len(User.States.possible_states):
                self._current_state_id += 1
            return self.current_state

        def previous(self, read_only=False) -> State:
            if self._current_state_id > 0 and not read_only:
                self._current_state_id -= 1
            return self.current_state

        def to_state(self, state: State) -> State:
            if state in User.States.possible_states:
                self._current_state_id = User.States.possible_states.index(state)
            return self.current_state

        def reset(self) -> State:
            self._current_state_id = 0
            return self.current_state

    def __init__(self, user_id):
        self.state = User.States()
        self.user_id = user_id
        self.cached_results = {
            'genre': None, 'person': None, 'mpaa': None, 'actor': None, 'director': None
        }
        self.movie_candidates = []
        self.movie_with_ratings = []


class DialogueManager:

    def __init__(self):
        self.users = {}

    def end_user_session(self, user_id):
        # user = self.users.get(user_id)
        # user.state.reset()
        self.users.pop(user_id)

    def utterance(self, user_id, message: dict) -> list:

        # obtain a user object that represents the current user
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        user = self.users[user_id]

        # parsing the incoming message
        input_text = message.get('text')

        # start of the conversation
        print('current state: ', user.state.current_state)

        responses = []

        if user.state.current_state == State.INTRO:
            responses = [template_manager.get_sentence(state=user.state.current_state),
                         template_manager.get_sentence(state=user.state.next())]

            user.movie_candidates = titles

        # side information collection
        elif user.state.current_state in [State.GENRE,
                                          State.ACTOR,
                                          State.DIRECTOR,
                                          State.MPAA]:
            query, intent, entity = luisQuery.query(input_text)
            _, answered = luisIntent.map_intent(state=user.state.current_state.value, intent=intent,
                                                entities=entity, user_cache=user.cached_results)

            print('cached_results', user.cached_results)

            if not answered:
                responses = ["I do not understand your answer."]
            else:
                user.movie_candidates = filterMovies.filter_candidates(
                    state=user.state.current_state.value,
                    user_cache=user.cached_results,
                    user_tconst=user.movie_candidates
                )[0]
                print('movie candidates:\n', len(user.movie_candidates))

                user.state.next()
                responses = [
                    template_manager.get_sentence(state=user.state.current_state)
                ]




        # get movie recommendation
        print('cached_results', user.cached_results)

        if user.state.current_state is State.TELL:

            user.movie_with_ratings = tellCtrl.sort_by_rating(user.movie_candidates)
            responses += tellCtrl.to_text(user.movie_with_ratings)
            user.state.to_state(State.TELL1)
            responses += [template_manager.get_sentence(state=user.state.current_state)]

        elif user.state.current_state is State.TELL1:
            query, intent, entity = luisQuery.query(input_text)
            _, answered = luisIntent.map_intent(state=user.state.current_state.value, intent=intent,
                                                entities=entity, user_cache=user.cached_results)

            if user.cached_results['satisfied'] == 'Yes':  # if watched recommendation before
                user.state.to_state(State.TELL1_5)
            else:
                user.state.to_state(State.TELL2)
            responses = [template_manager.get_sentence(state=user.state.current_state)]

        elif user.state.current_state is State.TELL1_5:
            query, intent, entity = luisQuery.query(input_text)
            _, answered = luisIntent.map_intent(state=user.state.current_state.value, intent=intent,
                                                entities=entity, user_cache=user.cached_results)

            if user.cached_results['satisfied'] == 'Yes':  # want new recommendations
                user.movie_with_ratings.pop(0)
                if not user.movie_with_ratings:
                    responses = [no_recommendation, end_dialogue]
                    user.state.to_state(State.BYE)
                else:
                    responses = tellCtrl.to_text(user.movie_with_ratings)
                    user.state.to_State(State.TELL1)
                    responses += [template_manager.get_sentence(state=user.state.current_state)]
            else:
                responses = [end_dialogue]
                user.state.to_state(State.BYE)

        elif user.state.current_state is State.TELL2:
            query, intent, entity = luisQuery.query(input_text)
            _, answered = luisIntent.map_intent(state=user.state.current_state.value, intent=intent,
                                                entities=entity, user_cache=user.cached_results)

            if user.cached_results['satisfied'] == 'Yes':
                responses = [end_dialogue]
                user.state.to_state(State.BYE)
            else:
                user.movie_with_ratings.pop(0)
                if not user.movie_with_ratings:
                    responses = [no_recommendation, end_dialogue]
                    user.state.to_state(State.BYE)
                else:
                    responses = tellCtrl.to_text(user.movie_with_ratings)
                    user.state.to_tell1()
                    responses += [template_manager.get_sentence(state=user.state.current_state)]

        if user.state.current_state is State.BYE:
            self.end_user_session(user_id)

        print('RESPONSES:\n', responses)
        return responses

    def get_movies(self, user_id):
        pass




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
            passiveResp[userid] = queue.Queue()
            question = template_manager.get_sentence(state='intro', is_dynamic=False)
            question2 = template_manager.get_sentence(state=state[userid][-1], is_dynamic=False)
            print(question)
            passiveResp[userid].put(question)
            passiveResp[userid].put(question2)

            nomatch[userid] = False
            history[userid] = []
            textHistory[userid] = []
            movie_with_ratings[userid] = []
            cache_results[userid] = {'genre': None, 'person': None, 'mpaa': None,'actor': None, 'director': None}
            curr_movie[userid] = None

            textHistory[userid].append(("C", question))
            history[userid].append((question, state[userid][-1]))
            return '', userid, 0, None

        query, intent, entity = luisQuery.query(text)
        #print "cache_results[userid] before luis", cache_results[userid]
        cache_results[userid], answered = luisIntent.map_intent(state[userid][-1], intent, entity,
                                                                cache_results[userid])
        #print "after", cache_results[userid]
        # cache_results[userid] = luisVerify.query(cache_results[userid])
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
                print("[DEBUG] cache_results: {}".format(curr_movie[userid]))
                question = template_manager.get_sentence(state=newState, is_dynamic=False)
                print(question)
                print(newState)


        # Append history
        history[userid].append((text, state[userid][-1]))
        history[userid].append((question, state[userid][-1]))
        passiveResp[userid].put(question)
        resp = passiveResp[userid].get()

        textHistory[userid].append(("U", text))
        textHistory[userid].append(("C", resp))

        # check for end state of bye, if so, send an end signal
        print("dialogueCtrl::state: {}".format(state[userid][-1]))
        signal = None
        # if state[userid][-1] == State.TELL:
        #     print "state is tell"
        #     signal = 'end'

        # if state[userid][-1] == State.BYE:
        #     print "state is bye"
        #     signal = 'end'

        return resp, userid, passiveResp[userid].qsize(), signal

    except ValueError as e:
        print("dialogueCtrl: {}".format(e))
        return '', userid, passiveResp[userid].qsize(), None


def initResources():
    global titles
    titles = []

    # Load question library
    try:
        template_manager.init_resources()
    except Exception as e:
        raise e

    # Init list of candidate movies - (relatively new 9-20-17)
    sqlstring = """SELECT tconst FROM title WHERE netflixid IS NOT NULL"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        titles.append(mov[0])

    print("[OK] Initialization of resources.")
    return


# def listen(userid):

    # resp = passiveResp[userid].get()
    # textHistory[userid].append(("C", resp))
    # return resp, userid, passiveResp[userid].qsize()

def listen(userid):
    # while not passiveResp[userid].qsize():
    #     continue
    resp = passiveResp[userid].get(True)
    print(resp)
    textHistory[userid].append(("C", resp))
    return resp, userid, passiveResp[userid].qsize()


def dialogueIdle(userid, debug=False):
    global active, passiveResp, has_recommended_movie, nomatch, movie_with_ratings
    if not state[userid]:
        return
    elif len(state[userid]) < 2:
        #print "len(state[userid]) < 2"
        titles_user[userid] = titles
        return

    print("dialogueIdle::state: {}".format(state[userid]))
    # Logic
    if state[userid][-1] == State.BYE:
        chatlogger.logToFile(textHistory[userid], userid)
        return

    if state[userid][-2] == State.BYE:
        return

    # if state[userid][-1] != State.TELL2:
    #     titles_user[userid], match = filterMovies.query(state[userid][-2], cache_results[userid],
    #                                                titles_user[userid])
    #     if not nomatch[userid] and not match:
    #         nomatch[userid] = True
    #         passiveResp[userid].put(notperfect_string, False)

    if state[userid][-1] == State.TELL:
        try:
            #movieWithRatings[userid] = tellCtrl.query(cache_results[userid], titles_user[userid], scoreweights, history[userid])
            print(titles_user[userid])
            movie_with_ratings[userid] = tellCtrl.sort_by_rating(titles_user[userid])
            movie_with_ratings[userid]
            outputlist = tellCtrl.to_text(movie_with_ratings[userid])
            # TODO: Workaround for the out of order bug, by making it a single json response
            # outputString = "<br><br>".join(outputlist)
            for each in outputlist:
                # print "Each: \n{}".format(each)
                passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners

        except Exception as e:
            print("Error at dialogueCtrl::164: {}".format(e))
        #chatlogger.logToFile(textHistory[userid], userid)
        state[userid].append(State.TELL1)
        question = template_manager.get_sentence(state=State.TELL1, is_dynamic=False)
        passiveResp[userid].put(question, False)
        #cache_results[userid]['satisfied'][-1] = None

    elif state[userid][-1] == State.TELL1:
        if cache_results[userid]['satisfied'] == 'Yes':  # if watched recommendation before
            state[userid].append(State.TELL1_5)
            question = template_manager.get_sentence(state=State.TELL1_5, is_dynamic=False)
            passiveResp[userid].put(question, False)
        else:
            state[userid].append(State.TELL2)
            question = template_manager.get_sentence(state=State.TELL2, is_dynamic=False)
            passiveResp[userid].put(question, False)

    elif state[userid][-1] == State.TELL1_5:
        if cache_results[userid]['satisfied'] == 'Yes':  # want new recommendations
            movie_with_ratings[userid].pop(0)
            if not movie_with_ratings[userid]:
                passiveResp[userid].put(no_recommendation)
                passiveResp[userid].put(end_dialogue)
                state[userid].append(State.BYE)
                return
            print(movie_with_ratings[userid])
            outputlist = tellCtrl.to_text(movie_with_ratings[userid])
            for each in outputlist:
                # print "Each: \n{}".format(each)
                passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
            # passiveResp[userid].put(end_dialogue)
            state[userid].append(State.TELL1)
            question = template_manager.get_sentence(state=State.TELL1, is_dynamic=False)
            passiveResp[userid].put(question)
        else:
            passiveResp[userid].put(end_dialogue)
            state[userid].append(State.BYE)


    elif state[userid][-1] == State.TELL2:
        if cache_results[userid]['satisfied'] == 'Yes':
            passiveResp[userid].put(end_dialogue)
            state[userid].append(State.BYE)
        else:
            movie_with_ratings[userid].pop(0)
            if not movie_with_ratings[userid]:
                passiveResp[userid].put(no_recommendation)
                passiveResp[userid].put(end_dialogue)
                state[userid].append(State.BYE)
                return
            print(movie_with_ratings[userid])
            outputlist = tellCtrl.to_text(movie_with_ratings[userid])
            for each in outputlist:
                # print "Each: \n{}".format(each)
                passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
            # passiveResp[userid].put(end_dialogue)
            state[userid].append(State.TELL1)
            question = template_manager.get_sentence(state=State.TELL1, is_dynamic=False)
            passiveResp[userid].put(question)

    else:
        #print "title_user before\n", len(titles_user[userid])
        titles_user[userid] = filterMovies.filter_candidates(state[userid][-2], cache_results[userid], titles_user[userid])[0]
        #print "title_user after\n", len(titles_user[userid])

    if has_recommended_movie and debug and not passiveResp[userid]:
        # print "textHistory: {}".format(textHistory[userid])
        has_recommended_movie = False

    return


def dialogueTest():
    print('[OK] Start dialogue test')
    # import pprint
    # pp = pprint.PrettyPrinter(depth=6)

    initResources()
    # state["599f6b6e8a3fd"] = ["genre"]
    # history["599f6b6e8a3fd"] = []
    dialogueCtrl('debug')
    print('[OK] End dialogue test')
    return


    # dialogueTest()
