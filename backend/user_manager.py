from enum import Enum

import dialogue_manager as dm


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

    def __init__(self, user_id):
        self.state = dm.DialogueManager.States()
        self.user_id = user_id

        # TODO: Load session data
        self.session_data = User.SessionData()
        self.chatbot_usage_count = 0
