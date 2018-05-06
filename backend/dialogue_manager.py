# Kevin Jesse
# @author kevin.r.jesse@gmail.com
#
# import logging
# import sys

"""
Controls the dialogue chatbox. Dialogue control is called from server.py
"""

import database_connect
import luis
import movie_manager as mm
import template_manager as tm
import user_manager as um
from state_manager import StateManager, State

cur = database_connect.db_connect()

# Global Flags

server_mode = 'messenger'
hypothesis = 'online'


def init_resources(mode: str, mode_hypothesis: str):
    global server_mode, hypothesis
    server_mode = mode
    hypothesis = mode_hypothesis

    # Load question library
    try:
        tm.init_resources()
        mm.init_resources()
        luis.init_resource()
    except Exception as e:
        raise e

    print("[OK] Initialization of resources.")
    return


class DialogueManager:

    def __init__(self):
        self.current_users = {}
        self.possible_states = [
            State(name='intro', next_state=lambda: 'genre'),
            State(name='genre', next_state=lambda: 'actor'),
            State(name='actor', next_state=lambda: 'director'),
            State(name='director', next_state=lambda: 'mpaa'),
            State(name='mpaa', next_state=lambda: 'thinking'),
            State(name='thinking', next_state=lambda: 'tell')
        ]
        if hypothesis == 'online':
            self.possible_states += [
                State(name='tell', next_state=lambda: 'good_recommendation'),
                State(name='good_recommendation', next_state=lambda is_good: 'has_watched' if is_good else 'thinking')
            ]
        elif hypothesis == 'mf':
            self.possible_states += [
                State(name='tell', next_state=lambda: 'has_watched'),
            ]

        self.possible_states += [
            State(name='has_watched',
                  next_state=lambda has_watched: 'has_watched_yes' if has_watched else 'has_watched_no'),
            State(name='has_watched_yes',
                  next_state=lambda want_new_rec: 'thinking' if want_new_rec else 'bye',
                  template_sentence_query={
                      'state': 'has_watched_response',
                      'options': 'yes'
                  }),
            State(name='has_watched_no',
                  next_state=lambda like_movie: 'bye' if like_movie else 'thinking',
                  template_sentence_query={
                      'state': 'has_watched_response',
                      'options': 'no'
                  }),
            State(name='movie_pop_check',
                  next_state=lambda has_next_movie: 'tell' if has_next_movie else 'bye'),
            State(name='bye', next_state=lambda: None,
                  template_sentence_query={
                      'options': server_mode
                  })
        ]

    def end_user_session(self, user_id):
        # user = self.current_users.get(user_id)
        # user.state.reset()
        # print("end user session", self.current_users)
        if user_id in self.current_users:
            user = self.current_users.get(user_id)
            user.chatbot_usage_count = 0
            self.current_users.pop(user_id)

    def utterance(self, user_id: str, message: dict) -> list:

        # parsing the incoming message
        input_text = message.get('text')
        if input_text is None or '':
            return ['']

        # get utterance based on state

        # obtain a user object that represents the current user
        if user_id not in self.current_users:
            self.current_users[user_id] = um.User(user_id,
                                                  state_manager=StateManager(self.possible_states),
                                                  mode_hypothesis=hypothesis)
        user: um.User = self.current_users[user_id]

        print("current state:", user.states.current_state.name)

        responses = []

        if user.states.current_state.name == 'intro':
            # print(user.states.current_state.template_sentence_query)
            responses = [user.states.current_state.utterance(),
                         user.states.next_state().utterance()]  # genre
            print('movie candidates:\n', len(user.current_session.movie_manager.movie_candidates))

        elif user.states.current_state.name in ['genre', 'actor', 'director', 'mpaa']:
            query, intent, entities = luis.query(input_text)

            answered = luis.parse_entities(
                current_state=user.states.current_state.name,
                luis_intent=intent,
                luis_entities=entities,
                user_session=user.current_session
            )
            print("answered", answered)
            print('user_session_data', user.current_session.movie_preferences)

            if not answered:
                responses = [tm.get_sentence(
                    dialogue_type='messages', options='do_not_understand'
                )]
            else:
                if hypothesis == 'cf':
                    user.current_session.movie_manager.filter_candidates(
                        state=user.states.current_state.name,
                    )
                    if user.current_session.movie_manager.movie_candidates:
                        print("setting movie candidates", len(user.current_session.movie_manager.movie_candidates))

                    print('movie candidates:\n', len(user.current_session.movie_manager.movie_candidates))

                user.states.next_state()
                responses = user.states.current_state.utterance()

        if user.states.current_state.name == 'thinking':
            # if user.states.current_state.previous_state == 'mpaa':
            user.states.next_state()

        if user.states.current_state.name == 'tell':
            if hypothesis == 'cf':
                movie, response = user.current_session.movie_manager.utterance()
                responses = response
                user.current_session.new_recommendation(movie=movie)
            elif hypothesis == 'mf':
                user.current_session.movie_manager.matrix_recommend()

            user.states.next_state()
            responses += [user.states.current_state.utterance()]

        elif user.states.current_state.name in ['good_recommendation',
                                                'has_watched',
                                                'has_watched_yes',
                                                'has_watched_no']:
            _, intent, _ = luis.query(input_text)
            answer = luis.parse_yes_no(luis_intent=intent)
            print("luis yes no answer", answer)

            if answer is None or answer is luis.LuisYesNo.NO_PREF:
                responses = [tm.get_sentence(dialogue_type='messages',
                                             options='do_not_understand'),
                             user.states.current_state.utterance()]

            else:
                if user.states.current_state.name == 'good_recommendation':
                    if answer is luis.LuisYesNo.YES:
                        user.current_session.edit_last_recommendation(good_recommendation=True)
                        # TODO: get new movie
                        user.states.next_state(is_good=True)
                        responses = user.states.current_state.utterance()
                    elif answer is luis.LuisYesNo.NO:
                        user.current_session.edit_last_recommendation(good_recommendation=False)
                        # TODO: get new movie
                        user.states.next_state(is_good=False)
                        responses = user.states.current_state.utterance()
                elif user.states.current_state.name == 'has_watched':
                    if answer is luis.LuisYesNo.YES:
                        user.current_session.edit_last_recommendation(has_watched_before=True)
                        user.states.next_state(has_watched=True)
                        responses = user.states.current_state.utterance()
                    elif answer is luis.LuisYesNo.NO:
                        user.current_session.edit_last_recommendation(has_watched_before=False)
                        user.states.next_state(has_watched=False)
                        responses = user.states.current_state.utterance()
                elif user.states.current_state.name == 'has_watched_yes':
                    if answer is luis.LuisYesNo.YES:
                        user.current_session.edit_last_recommendation(is_satisfied=False)
                        user.states.next_state(want_new_rec=True)
                        # responses = user.states.current_state.utterance()
                    elif answer is luis.LuisYesNo.NO:
                        user.current_session.edit_last_recommendation(is_satisfied=True)
                        user.states.next_state(want_new_rec=False)
                        responses = user.states.current_state.utterance()
                elif user.states.current_state.name == 'has_watched_no':
                    if answer is luis.LuisYesNo.YES:
                        user.current_session.edit_last_recommendation(is_satisfied=True)
                        user.states.next_state(like_movie=True)
                        responses = user.states.current_state.utterance()
                    elif answer is luis.LuisYesNo.NO:
                        user.current_session.edit_last_recommendation(is_satisfied=False)
                        user.states.next_state(like_movie=False)
                        # responses = user.states.current_state.utterance()

        if user.states.current_state.name == 'thinking':
            if user.states.current_state.previous_state in ['has_watched_yes', 'has_watched_no']:
                user.current_session.movie_manager.movies_with_ratings.pop(0)
                if user.current_session.movie_manager.movies_with_ratings:
                    user.states.next_state()
                else:
                    responses += [tm.get_sentence(dialogue_type='messages', options='no_recommendation'),
                                  user.states.to_state('bye').utterance()]

        if user.states.current_state == 'bye':
            self.end_user_session(user_id)

        return [responses] if type(responses) is str else responses

    # def utterance(self, user_id: str, message: dict) -> list:
    #
    #     # obtain a user object that represents the current user
    #     if user_id not in self.current_users:
    #         self.current_users[user_id] = User(user_id)
    #     user = self.current_users[user_id]
    #
    #     # print("Current users", self.current_users)
    #
    #     # parsing the incoming message
    #     input_text = message.get('text')
    #     if input_text is None or '':
    #         return ['']
    #
    #     # start of the conversation
    #     print('current state: ', user.state.current_state)
    #
    #     responses = []
    #
    #     print('server_mode: ', server_mode)
    #
    #     if user.state.current_state == State.INTRO:
    #         if user.chatbot_usage_count > 0:
    #             responses = [
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     state=user.state.current_state
    #                 ),
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     state=user.state.next()
    #                 )
    #             ] if server_mode != 'cobot' else [
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     state=user.state.next()
    #                 )
    #             ]
    #         else:
    #             responses = [
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     usage_count=1,
    #                     state=user.state.current_state
    #                 )
    #             ]
    #             user.state.next()
    #         print(responses)
    #
    #         user.movie_candidates = titles
    #
    #     # side information collection
    #     elif user.state.current_state in [State.GENRE,
    #                                       State.ACTOR,
    #                                       State.DIRECTOR,
    #                                       State.MPAA]:
    #         query, intent, entities = luis.query(input_text)
    #
    #         answered = luis.parse_entities(
    #             current_state=user.state.current_state,
    #             luis_intent=intent,
    #             luis_entities=entities,
    #             user_session=user.session_data
    #         )
    #         print("answered", answered)
    #         print('user_session_data', user.session_data.movie_preferences)
    #
    #         if not answered:
    #             responses = [template_manager.get_sentence(
    #                 dialogue_type=template_manager.DialogueType.MESSAGES,
    #                 options='do_not_understand'
    #             )]
    #         else:
    #             movie_candidates = movie_manager.filter_candidates(
    #                 state=user.state.current_state.value,
    #                 user_session_data=user.session_data,
    #                 movie_candidates=user.movie_candidates
    #             )
    #             if movie_candidates is not None:
    #                 print("setting movie candidates", len(movie_candidates))
    #                 user.movie_candidates = movie_candidates
    #
    #             print('movie candidates:\n', len(user.movie_candidates))
    #
    #             # move to the next state
    #             # if at the last info collection state, shift to thinking
    #             # TODO: Migrate thinking from a state to a message
    #             user.state.next()
    #             responses = [
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     state=user.state.current_state
    #                 )
    #             ]
    #
    #     if user.state.current_state is State.THINKING:
    #         user.state.next()
    #
    #     # get movie recommendation
    #     print('user_session_data', user.session_data)
    #
    #     # output recommendation
    #     if user.state.current_state is State.TELL:  # Actually telling the movie
    #
    #         user.movie_with_ratings = tellCtrl.sort_by_rating(user.movie_candidates)
    #         movie, response = tellCtrl.to_text(user.movie_with_ratings)
    #         responses = response
    #         user.session_data.new_recommendation(movie=movie)
    #
    #         user.state.to_state(State.HAS_WATCHED if self.mode != 'cobot' else State.IS_SATISFIED)
    #         responses += [template_manager.get_sentence(
    #             dialogue_type=template_manager.DialogueType.UTTERANCES,
    #             state=user.state.current_state
    #         )]
    #
    #     elif user.state.current_state in [State.HAS_WATCHED,
    #                                       State.HAS_WATCHED_RESPONSE]:  # ask if user has seen movie
    #         _, intent, _ = luis.query(input_text)
    #         answer = luis.parse_yes_no(luis_intent=intent)
    #         print("luis yes no answer", answer)
    #
    #         if answer is None or answer is luis.LuisYesNo.NO_PREF:
    #             # print("dshfoihsdfiosdh")
    #             responses += [
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.MESSAGES,
    #                     options='do_not_understand'
    #                 ),
    #                 template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     state=user.state.current_state
    #                 )
    #             ]
    #
    #         else:
    #             if user.state.current_state is State.HAS_WATCHED:
    #                 if answer is luis.LuisYesNo.YES:
    #                     user.session_data.edit_last_recommendation(has_watched_before=True)
    #                     user.state.to_state(State.HAS_WATCHED_RESPONSE)
    #                     responses += [template_manager.get_sentence(
    #                         dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                         state=user.state.current_state,
    #                         options='yes'
    #                     )]
    #                 elif answer is luis.LuisYesNo.NO:
    #                     user.session_data.edit_last_recommendation(has_watched_before=False)
    #                     user.state.to_state(State.HAS_WATCHED_RESPONSE)
    #                     responses += [template_manager.get_sentence(
    #                         dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                         state=user.state.current_state,
    #                         options='no'
    #                     )]
    #
    #             elif user.state.current_state is State.HAS_WATCHED_RESPONSE:
    #                 has_watched_before = user.session_data.recommendations[-1]['has_watched_before']
    #                 if (has_watched_before and answer is luis.LuisYesNo.NO) or \
    #                         (not has_watched_before and answer is luis.LuisYesNo.YES):
    #                     user.session_data.edit_last_recommendation(is_satisfied=True)
    #                     responses = [template_manager.get_sentence(
    #                         dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                         state=State.BYE,
    #                         options=self.mode
    #                     )]
    #                     user.state.to_state(State.BYE)
    #
    #                 else:
    #                     user.session_data.edit_last_recommendation(is_satisfied=False)
    #                     user.state.to_state(State.TELL)
    #                     user.movie_with_ratings.pop(0)
    #                     if user.movie_with_ratings:
    #                         responses = tellCtrl.to_text(user.movie_with_ratings)
    #                         user.state.to_State(State.HAS_WATCHED)
    #                         responses += [template_manager.get_sentence(
    #                             dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                             state=user.state.current_state
    #                         )]
    #                     else:
    #                         responses = [
    #                             template_manager.get_sentence(
    #                                 dialogue_type=template_manager.DialogueType.MESSAGES,
    #                                 options='no_recommendation'
    #                             ),
    #                             template_manager.get_sentence(
    #                                 dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                                 state=State.BYE,
    #                                 options=self.mode
    #                             )
    #                         ]
    #                         user.state.to_state(State.BYE)
    #
    #     elif user.state.current_state is State.IS_SATISFIED:
    #         _, intent, _ = luis.query(input_text)
    #         answer = luis.parse_yes_no(luis_intent=intent)
    #
    #         if answer is luis.LuisYesNo.YES:
    #             user.session_data.edit_last_recommendation(is_satisfied=True)
    #             user.state.to_state(State.BYE)
    #             print("Is satisfied yes", user.state.current_state)
    #             responses += [template_manager.get_sentence(
    #                 dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                 state=State.BYE,
    #                 options=self.mode
    #             )]
    #         elif answer is luis.LuisYesNo.NO:
    #             user.session_data.edit_last_recommendation(is_satisfied=False)
    #             user.state.to_state(State.TELL)
    #             user.movie_with_ratings.pop(0)
    #             if user.movie_with_ratings:
    #                 responses = tellCtrl.to_text(user.movie_with_ratings)
    #                 user.state.to_State(State.IS_SATISFIED)
    #                 responses += [template_manager.get_sentence(
    #                     dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                     state=user.state.current_state
    #                 )]
    #             else:
    #                 responses = [
    #                     template_manager.get_sentence(
    #                         dialogue_type=template_manager.DialogueType.MESSAGES,
    #                         options='no_recommendation'
    #                     ),
    #                     template_manager.get_sentence(
    #                         dialogue_type=template_manager.DialogueType.UTTERANCES,
    #                         state=State.BYE,
    #                         options=self.mode
    #                     )
    #                 ]
    #                 user.state.to_state(State.BYE)
    #
    #     if user.state.current_state is State.BYE:
    #         self.end_user_session(user_id)
    #         # user.chatbot_usage_count += 1
    #
    #     print('RESPONSES:\n', responses)
    #     return responses

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
