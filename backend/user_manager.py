from typing import List

import state_manager as sm


class SessionData:
    def __init__(self, mode_hypothesis: str):
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


class User:

    states: sm.StateManager
    current_session: SessionData

    def __init__(self, user_id, state_manager: sm.StateManager, mode_hypothesis: str):
        self.states = state_manager
        self.user_id = user_id

        # TODO: Load session data
        self.current_session = SessionData(mode_hypothesis=mode_hypothesis)
        self.chatbot_usage_count = 0

    # @property
    # def states(self) -> sm.StateManager:
    #     return self._state_manager


class UserManager:

    def __init__(self, possible_states: List[sm.State]):
        self.possible_states = possible_states
        self.current_users = {}