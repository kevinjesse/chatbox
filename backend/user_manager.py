import json
import time
from typing import List

import state_manager as sm
import history_manager as hm


class SessionData:
    def __init__(self, mode_hypothesis: str):
        # History
        self.conversation = []

        self.movie_preferences = {
            'genre': [],
            'actor': [],
            'director': [],
            'mpaa': []
        }

        # NOTE: Do not modify this, use new_recommendation instead
        self.recommendations = []

        import movie_manager as mm
        self.movie_manager = mm.MovieManager(session_data=self)

    def new_recommendation(self, movie,
                           good_recommendation:bool=None,
                           has_watched_before: bool=None,
                           is_satisfied: bool=None):
        self.recommendations.append({
            'movie': movie,
            'good_recommendation': good_recommendation,
            'has_watched_before': has_watched_before,
            'is_satisfied': is_satisfied
        })

    def edit_last_recommendation(self,
                                 good_recommendation: bool=None,
                                 has_watched_before: bool=None,
                                 is_satisfied: bool=None):
        if good_recommendation is not None:
            self.recommendations[-1]['good_recommendation'] = good_recommendation
        if has_watched_before is not None:
            self.recommendations[-1]['has_watched_before'] = has_watched_before
        if is_satisfied is not None:
            self.recommendations[-1]['is_satisfied'] = is_satisfied

    def insert_dialogue(self, sayer: str, utterance):
        self.conversation.append((sayer, utterance, time.time()))

    def to_dict(self) -> dict:
        return {
            'dialogue': [
                {
                    'timestamp': timestamp,
                    'sayer': sayer,
                    'utterance': utterance
                } for sayer, utterance, timestamp in self.conversation
            ],
            'movie_preferences': self.movie_preferences,
            'recommendations': self.recommendations
        }


class User:

    # states: sm.StateManager
    # current_session: SessionData

    def __init__(self, user_id, state_manager: sm.StateManager, mode: str, mode_hypothesis: str):
        self.states = state_manager
        self.user_id = user_id
        self.mode = mode
        self.mode_hypothesis = mode_hypothesis

        # TODO: Load session data
        self.current_session = SessionData(mode_hypothesis=self.mode_hypothesis)
        self.last_session = hm.last_user_history(self.user_id)

    def end_session(self):
        self._save_log()
        self.current_session = SessionData(mode_hypothesis=self.mode_hypothesis)

    def _save_log(self):
        hm.save_user_history(
            user_id=self.user_id,
            conversation=self.current_session.to_dict(),
            mode=self.mode,
            mode_hypothesis=self.mode_hypothesis
        )


class UserManager:

    def __init__(self, possible_states: List[sm.State]):
        self.possible_states = possible_states
        self.current_users = {}
