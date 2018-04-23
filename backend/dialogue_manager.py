# Kevin Jesse
# @author kevin.r.jesse@gmail.com
#
# import logging
# import sys

"""
Controls the dialogue chatbox. Dialogue control is called from server.py
"""

from enum import Enum

import database_connect
import filterMovies
import luis
import tellCtrl
import template_manager
from template_manager import State

cur = database_connect.db_connect()


class MoviePreferences(Enum):
    # 'genre': None, 'person': None, 'mpaa': None, 'actor': None, 'director': None
    GENRE = 'genre'
    ACTOR = 'actor'
    DIRECTOR = 'director'
    MPAA = 'mpaa'


class User:

    class SessionData:
        def __init__(self):
            self.movie_preferences = {
                MoviePreferences.GENRE: [],
                MoviePreferences.ACTOR: [],
                MoviePreferences.DIRECTOR: [],
                MoviePreferences.MPAA: []
            }

            # NOTE: Do not modify this, use new_recommendation instead
            self.recommendations = []

        def new_recommendation(self, movie, has_watched_before: bool=None, is_satisfied: bool=None):
            self.recommendations.append({
                'movie': movie, 'has_watched_before': has_watched_before, 'is_satisfied': is_satisfied
            })

        def edit_last_recommendation(self, has_watched_before: bool=None, is_satisfied:bool=None):
            if has_watched_before is not None:
                self.recommendations[-1]['has_watched_before'] = has_watched_before
            if is_satisfied is not None:
                self.recommendations[-1]['is_satisfied'] = is_satisfied

    def __init__(self, user_id):
        self.state = DialogueManager.States()
        self.user_id = user_id

        # TODO: Load session data
        self.session_data = User.SessionData()

        self.movie_candidates = []
        self.movie_with_ratings = []


class DialogueManager:

    class States:
        possible_states = [State.INTRO,
                           State.GENRE,
                           State.ACTOR,
                           State.DIRECTOR,
                           State.MPAA,
                           State.THINKING,
                           State.TELL,
                           State.HAS_WATCHED,
                           State.HAS_WATCHED_RESPONSE,
                           State.BYE]

        def __init__(self):
            self._current_state_id = 0

        @property
        def current_state(self) -> State:
            return DialogueManager.States.possible_states[self._current_state_id]

        def next(self) -> State:
            if self._current_state_id < len(DialogueManager.States.possible_states):
                self._current_state_id += 1
            return self.current_state

        def previous(self, read_only=False) -> State:
            if self._current_state_id > 0 and not read_only:
                self._current_state_id -= 1
            return self.current_state

        def to_state(self, state: State) -> State:
            if state in DialogueManager.States.possible_states:
                self._current_state_id = DialogueManager.States.possible_states.index(state)
            return self.current_state

        def reset(self) -> State:
            self._current_state_id = 0
            return self.current_state

    def __init__(self, api_type):
        self.current_users = {}
        self.api_type = api_type

    def end_user_session(self, user_id):
        # user = self.current_users.get(user_id)
        # user.state.reset()
        self.current_users.pop(user_id)

    def utterance(self, user_id, message: dict) -> list:

        # obtain a user object that represents the current user
        if user_id not in self.current_users:
            self.current_users[user_id] = User(user_id)
        user = self.current_users[user_id]

        # parsing the incoming message
        input_text = message.get('text')

        # start of the conversation
        print('current state: ', user.state.current_state)

        responses = []

        if user.state.current_state == State.INTRO:
            responses = [
                template_manager.get_sentence(
                    dialogue_type=template_manager.DialogueType.UTTERANCES,
                    state=user.state.current_state
                ),
                template_manager.get_sentence(
                    dialogue_type=template_manager.DialogueType.UTTERANCES,
                    state=user.state.next()
                )
            ]

            user.movie_candidates = titles

        # side information collection
        elif user.state.current_state in [State.GENRE,
                                          State.ACTOR,
                                          State.DIRECTOR,
                                          State.MPAA]:
            query, intent, entities = luis.query(input_text)

            answered = luis.parse_entities(
                current_state=user.state.current_state,
                luis_intent=intent,
                luis_entities=entities,
                user_session=user.session_data
            )

            print('user_session_data', user.session_data)

            if not answered:
                responses = [template_manager.get_sentence(
                    dialogue_type=template_manager.DialogueType.MESSAGES,
                    options='do_not_understand'
                )]
            else:
                user.movie_candidates = filterMovies.filter_candidates(
                    state=user.state.current_state.value,
                    user_cache=user.cached_results,
                    user_tconst=user.movie_candidates
                )[0]
                print('movie candidates:\n', len(user.movie_candidates))

                # move to the next state
                # if at the last info collection state, shift to thinking
                # TODO: Migrate thinking from a state to a message
                user.state.next()
                responses = [
                    template_manager.get_sentence(state=user.state.current_state)
                ]

        # get movie recommendation
        print('user_session_data', user.session_data)

        # output recommendation
        if user.state.current_state is State.TELL:  # Actually telling the movie

            user.movie_with_ratings = tellCtrl.sort_by_rating(user.movie_candidates)
            movie, response = tellCtrl.to_text(user.movie_with_ratings)
            responses += response
            user.session_data.new_recommendation(movie=movie)

            user.state.to_state(State.HAS_WATCHED)
            responses += [template_manager.get_sentence(state=user.state.current_state)]

        elif user.state.current_state in [State.HAS_WATCHED,
                                          State.HAS_WATCHED_RESPONSE]:  # ask if user has seen movie
            _, intent, _ = luis.query(input_text)
            answer = luis.parse_yes_no(luis_intent=intent)

            if answer is None or luis.LuisYesNo.NO_PREF:
                responses += [
                    template_manager.get_sentence(
                        dialogue_type=template_manager.DialogueType.MESSAGES,
                        options='do_not_understand'
                    ),
                    template_manager.get_sentence(
                        dialogue_type=template_manager.DialogueType.UTTERANCES,
                        state=user.state.current_state
                    )
                ]

            else:
                if user.state.current_state is State.HAS_WATCHED:
                    if answer is luis.LuisYesNo.YES:
                        user.session_data.edit_last_recommendation(has_watched_before=True)
                        user.state.to_state(State.HAS_WATCHED_RESPONSE)
                        responses += [template_manager.get_sentence(
                            dialogue_type=template_manager.DialogueType.UTTERANCES,
                            state=user.state.current_state,
                            options='yes'
                        )]
                    elif answer is luis.LuisYesNo.NO:
                        user.session_data.edit_last_recommendation(has_watched_before=False)
                        user.state.to_state(State.HAS_WATCHED_RESPONSE)
                        responses += [template_manager.get_sentence(
                            dialogue_type=template_manager.DialogueType.UTTERANCES,
                            state=user.state.current_state,
                            options='no'
                        )]

                elif user.state.current_state is State.HAS_WATCHED_RESPONSE:
                    has_watched_before = user.session_data.recommendations[-1]['has_watched_before']
                    if (has_watched_before and answer is luis.LuisYesNo.NO) or \
                            (not has_watched_before and answer is luis.LuisYesNo.YES):
                        user.session_data.edit_last_recommendation(is_satisfied=True)
                        responses = [template_manager.get_sentence(
                            dialogue_type=template_manager.DialogueType.UTTERANCES,
                            state=State.BYE,
                            options=self.api_type
                        )]
                        user.state.to_state(State.BYE)

                    else:
                        user.session_data.edit_last_recommendation(is_satisfied=False)
                        user.state.to_state(State.TELL)
                        user.movie_with_ratings.pop(0)
                        if user.movie_with_ratings:
                            responses = tellCtrl.to_text(user.movie_with_ratings)
                            user.state.to_State(State.HAS_WATCHED)
                            responses += [template_manager.get_sentence(
                                dialogue_type=template_manager.DialogueType.UTTERANCES,
                                state=user.state.current_state
                            )]
                        else:
                            responses = [
                                template_manager.get_sentence(
                                    dialogue_type=template_manager.DialogueType.MESSAGES,
                                    options='no_recommendation'
                                ),
                                template_manager.get_sentence(
                                    dialogue_type=template_manager.DialogueType.UTTERANCES,
                                    state=State.BYE,
                                    options=self.api_type
                                )
                            ]
                            user.state.to_state(State.BYE)

        if user.state.current_state is State.BYE:
            self.end_user_session(user_id)

        print('RESPONSES:\n', responses)
        return responses

    def get_movies(self, user_id):
        pass


# # dialogueCtrl() controls dialogue flow with socket
# def dialogueCtrl(input_json):
#     """
#     dialogueCtrl takes in data (User input), sends to dialogue logic, gets response, and returns response back to socket
#     """
#     try:
#         global state, history, textHistory, data, cache_results, curr_movie, scoreweights, passiveResp
#         js = json.loads(input_json)
#         userid = js['id']
#         text = js['text']
#         mode = js['mode'] == "true"
#
#         if mode:
#             signal = "listen"
#             a, b, c = listen(userid)
#             return a, b, c, signal
#
#         output = ''
#         question = ''
#         if userid not in state or text == '':
#             # If this is a new user
#             state[userid] = ["genre", ]
#             # TODO: Substitute temp replacement with actual recommendations
#             replacement_genre = ["Action", "Comedy", "Sci-fi"]
#             passiveResp[userid] = queue.Queue()
#             question = template_manager.get_sentence(state='intro', is_dynamic=False)
#             question2 = template_manager.get_sentence(state=state[userid][-1], is_dynamic=False)
#             print(question)
#             passiveResp[userid].put(question)
#             passiveResp[userid].put(question2)
#
#             nomatch[userid] = False
#             history[userid] = []
#             textHistory[userid] = []
#             movie_with_ratings[userid] = []
#             cache_results[userid] = {'genre': None, 'person': None, 'mpaa': None,'actor': None, 'director': None}
#             curr_movie[userid] = None
#
#             textHistory[userid].append(("C", question))
#             history[userid].append((question, state[userid][-1]))
#             return '', userid, 0, None
#
#         query, intent, entity = luis.query(text)
#         #print "cache_results[userid] before luis", cache_results[userid]
#         cache_results[userid], answered = luisIntent.map_intent(state[userid][-1], intent, entity,
#                                                                 cache_results[userid])
#         #print "after", cache_results[userid]
#         # cache_results[userid] = luisVerify.query(cache_results[userid])
#         if not answered:
#             # if do not understand utterance because intent is incorrect, try to find with entities
#             passiveResp[userid].put("I do not understand your answer. ")
#             question = history[userid][-1][0]
#         else:
#             # will change state machine to class object
#             if state[userid][-1] in q_order:
#                 if not q_order.index(state[userid][-1]) == len(q_order) - 1:
#                     newState = q_order[q_order.index(state[userid][-1]) + 1]
#                 else:
#                     newState = state[userid][-1]
#                 state[userid].append(newState)
#                 print("[DEBUG] cache_results: {}".format(curr_movie[userid]))
#                 question = template_manager.get_sentence(state=newState, is_dynamic=False)
#                 print(question)
#                 print(newState)
#
#
#         # Append history
#         history[userid].append((text, state[userid][-1]))
#         history[userid].append((question, state[userid][-1]))
#         passiveResp[userid].put(question)
#         resp = passiveResp[userid].get()
#
#         textHistory[userid].append(("U", text))
#         textHistory[userid].append(("C", resp))
#
#         # check for end state of bye, if so, send an end signal
#         print("dialogueCtrl::state: {}".format(state[userid][-1]))
#         signal = None
#         # if state[userid][-1] == State.TELL:
#         #     print "state is tell"
#         #     signal = 'end'
#
#         # if state[userid][-1] == State.BYE:
#         #     print "state is bye"
#         #     signal = 'end'
#
#         return resp, userid, passiveResp[userid].qsize(), signal
#
#     except ValueError as e:
#         print("dialogueCtrl: {}".format(e))
#         return '', userid, passiveResp[userid].qsize(), None


def init_resources():
    global titles
    titles = []

    # Load question library
    try:
        template_manager.init_resources()
        luis.init_resource()
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


# # def listen(userid):
#
#     # resp = passiveResp[userid].get()
#     # textHistory[userid].append(("C", resp))
#     # return resp, userid, passiveResp[userid].qsize()
#
# def listen(userid):
#     # while not passiveResp[userid].qsize():
#     #     continue
#     resp = passiveResp[userid].get(True)
#     print(resp)
#     textHistory[userid].append(("C", resp))
#     return resp, userid, passiveResp[userid].qsize()
#
#
# def dialogueIdle(userid, debug=False):
#     global active, passiveResp, has_recommended_movie, nomatch, movie_with_ratings
#     if not state[userid]:
#         return
#     elif len(state[userid]) < 2:
#         #print "len(state[userid]) < 2"
#         titles_user[userid] = titles
#         return
#
#     print("dialogueIdle::state: {}".format(state[userid]))
#     # Logic
#     if state[userid][-1] == State.BYE:
#         chatlogger.logToFile(textHistory[userid], userid)
#         return
#
#     if state[userid][-2] == State.BYE:
#         return
#
#     # if state[userid][-1] != State.TELL2:
#     #     titles_user[userid], match = filterMovies.query(state[userid][-2], cache_results[userid],
#     #                                                titles_user[userid])
#     #     if not nomatch[userid] and not match:
#     #         nomatch[userid] = True
#     #         passiveResp[userid].put(notperfect_string, False)
#
#     if state[userid][-1] == State.TELL:
#         try:
#             #movieWithRatings[userid] = tellCtrl.query(cache_results[userid], titles_user[userid], scoreweights, history[userid])
#             print(titles_user[userid])
#             movie_with_ratings[userid] = tellCtrl.sort_by_rating(titles_user[userid])
#             movie_with_ratings[userid]
#             outputlist = tellCtrl.to_text(movie_with_ratings[userid])
#             # TODO: Workaround for the out of order bug, by making it a single json response
#             # outputString = "<br><br>".join(outputlist)
#             for each in outputlist:
#                 # print "Each: \n{}".format(each)
#                 passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
#
#         except Exception as e:
#             print("Error at dialogueCtrl::164: {}".format(e))
#         #chatlogger.logToFile(textHistory[userid], userid)
#         state[userid].append(State.TELL1)
#         question = template_manager.get_sentence(state=State.TELL1, is_dynamic=False)
#         passiveResp[userid].put(question, False)
#         #cache_results[userid]['satisfied'][-1] = None
#
#     elif state[userid][-1] == State.TELL1:
#         if cache_results[userid]['satisfied'] == 'Yes':  # if watched recommendation before
#             state[userid].append(State.TELL1_5)
#             question = template_manager.get_sentence(state=State.TELL1_5, is_dynamic=False)
#             passiveResp[userid].put(question, False)
#         else:
#             state[userid].append(State.TELL2)
#             question = template_manager.get_sentence(state=State.TELL2, is_dynamic=False)
#             passiveResp[userid].put(question, False)
#
#     elif state[userid][-1] == State.TELL1_5:
#         if cache_results[userid]['satisfied'] == 'Yes':  # want new recommendations
#             movie_with_ratings[userid].pop(0)
#             if not movie_with_ratings[userid]:
#                 passiveResp[userid].put(no_recommendation)
#                 passiveResp[userid].put(end_dialogue)
#                 state[userid].append(State.BYE)
#                 return
#             print(movie_with_ratings[userid])
#             outputlist = tellCtrl.to_text(movie_with_ratings[userid])
#             for each in outputlist:
#                 # print "Each: \n{}".format(each)
#                 passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
#             # passiveResp[userid].put(end_dialogue)
#             state[userid].append(State.TELL1)
#             question = template_manager.get_sentence(state=State.TELL1, is_dynamic=False)
#             passiveResp[userid].put(question)
#         else:
#             passiveResp[userid].put(end_dialogue)
#             state[userid].append(State.BYE)
#
#
#     elif state[userid][-1] == State.TELL2:
#         if cache_results[userid]['satisfied'] == 'Yes':
#             passiveResp[userid].put(end_dialogue)
#             state[userid].append(State.BYE)
#         else:
#             movie_with_ratings[userid].pop(0)
#             if not movie_with_ratings[userid]:
#                 passiveResp[userid].put(no_recommendation)
#                 passiveResp[userid].put(end_dialogue)
#                 state[userid].append(State.BYE)
#                 return
#             print(movie_with_ratings[userid])
#             outputlist = tellCtrl.to_text(movie_with_ratings[userid])
#             for each in outputlist:
#                 # print "Each: \n{}".format(each)
#                 passiveResp[userid].put(each, False)  # see if slower puts results in order pulls from listeners
#             # passiveResp[userid].put(end_dialogue)
#             state[userid].append(State.TELL1)
#             question = template_manager.get_sentence(state=State.TELL1, is_dynamic=False)
#             passiveResp[userid].put(question)
#
#     else:
#         #print "title_user before\n", len(titles_user[userid])
#         titles_user[userid] = filterMovies.filter_candidates(state[userid][-2], cache_results[userid], titles_user[userid])[0]
#         #print "title_user after\n", len(titles_user[userid])
#
#     if has_recommended_movie and debug and not passiveResp[userid]:
#         # print "textHistory: {}".format(textHistory[userid])
#         has_recommended_movie = False
#
#     return
#
#
# def dialogueTest():
#     print('[OK] Start dialogue test')
#     # import pprint
#     # pp = pprint.PrettyPrinter(depth=6)
#
#     init_resources()
#     # state["599f6b6e8a3fd"] = ["genre"]
#     # history["599f6b6e8a3fd"] = []
#     dialogueCtrl('debug')
#     print('[OK] End dialogue test')
#     return
#
#
#     # dialogueTest()
