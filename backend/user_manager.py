from typing import List

import state_manager as sm


class SessionData:
    def __init__(self):
        self.movie_preferences = {
            'genre': [],
            'actor': [],
            'director': [],
            'mpaa': []
        }

        # NOTE: Do not modify this, use new_recommendation instead
        self.recommendations = []

        self.movie_candidates = []
        self.movie_with_ratings = []

    def new_recommendation(self, movie, has_watched_before: bool=None, is_satisfied: bool=None):
        self.recommendations.append({
            'movie': movie, 'has_watched_before': has_watched_before, 'is_satisfied': is_satisfied
        })

    def edit_last_recommendation(self, has_watched_before: bool=None, is_satisfied:bool=None):
        if has_watched_before is not None:
            self.recommendations[-1]['has_watched_before'] = has_watched_before
        if is_satisfied is not None:
            self.recommendations[-1]['is_satisfied'] = is_satisfied


class User:

    states: sm.StateManager
    session_data: SessionData

    def __init__(self, user_id, state_manager: sm.StateManager):
        self.states = state_manager
        self.user_id = user_id

        # TODO: Load session data
        self.session_data = SessionData()
        self.chatbot_usage_count = 0

    # @property
    # def states(self) -> sm.StateManager:
    #     return self._state_manager


class UserManager:

    def __init__(self, possible_states: List[sm.State]):
        self.possible_states = possible_states
        self.current_users = {}