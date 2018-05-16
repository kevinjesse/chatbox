#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import re
import enum
from typing import Tuple, Optional

import requests
from nltk.stem.snowball import SnowballStemmer

import database_connect

base_url = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/"
api_keys = {}


class LuisYesNo(enum.Enum):
    NO_PREF = 'NoPreference'
    YES = 'Yes'
    NO = 'No'


def init_resource():
    """
    Initialize luis module. Fetch api keys to Luis.
    :return: None
    """
    global api_keys
    try:
        cur = database_connect.connect()
        cur.execute("SELECT api_type, api_key FROM api")
        api_keys = dict(cur.fetchall())
    except Exception as e:
        raise e


def query(text: str) -> Tuple[str, str, str]:
    """
    Convenience func to query Luis
    :param text: user utterances
    :return:
    """
    r = requests.get(url=base_url + api_keys['luisid'], params={
        'subscription-key': api_keys['luis'],
        'spellCheck': True,
        'bing-spell-check-subscription-key': api_keys['bing1'],
        'verbose': False,
        'timezoneOffset': 0,
        'q': text.strip()
    })
    if r.status_code != 200:
        print("LUIS status code: ", r.status_code)
        return None, None, None
    json = r.json()
    print("Luis to_dict:", json)
    return json['query'], json['topScoringIntent'], json['entities']


def genre_spellcheck(user_input):
    """
    Custom spellchecking
    :param user_input: user input text
    :return: corrected text
    """
    stemmer = SnowballStemmer('english')

    genre_core = ['action', 'adventure', 'animation', 'biography', 'comedy', 'crime', 'documentary', 'drama',
                  'family', 'fantasy', 'film-noir', 'history', 'horror', 'music', 'musical', 'mystery',
                  'romance', 'sci-fi', 'sport', 'thriller', 'war', 'western']
    genre_stem = dict(zip([stemmer.stem(item)[:5] for item in genre_core], genre_core))
    genre_stem['romantic'] = 'romance'
    genre_stem['sci fi'] = 'sci-fi'
    genre_stem['science fiction'] = 'sci-fi'
    genre_stem['funny'] = 'comedy'
    genre_stem['love'] = 'romance'

    user_input = user_input.lower()
    if user_input in genre_stem:
        return genre_stem[user_input]
    else:
        parsed_input = stemmer.stem(user_input)[:5]
        output = genre_stem[parsed_input] if parsed_input in genre_stem else user_input
        return output


def parse_entities(current_state: str, luis_intent, luis_entities, user_session) -> bool:
    """
    Used to parse to_dict returned from Luis. Takes in user.SessionData object and modify its
    content directly to save what's being parsed.
    :param current_state: current dialogue state
    :param luis_intent:
    :param luis_entities:
    :param user_session: user.SessionData
    :return: bool indicating if Luis detects a valid response
    """
    # TODO: Better is_answered detection
    is_answered = True

    if parse_yes_no(luis_intent) is LuisYesNo.NO_PREF:
        is_answered = True
        return is_answered

    for entity in luis_entities:
        entity_type = _entity_type_from_luis_entity(entity.get('type'))
        if entity_type is None or entity_type != _luis_entity_from_state(current_state):
            is_answered = False
            continue

        if entity_type == 'year' or entity_type == 'duration':
            pass
        elif entity_type == 'genre':
            print('genre_input: {}'.format(entity['entity']))
            input_genre = genre_spellcheck(entity['entity'])
            print('genre_output: {}'.format(input_genre))

            user_session.movie_preferences['genre'].append(input_genre)

        elif entity_type == 'person':
            input_name = entity['entity'].title()
            if current_state is 'actor':
                user_session.movie_preferences['actor'].append(input_name)
            elif current_state is 'director':
                user_session.movie_preferences['director'].append(input_name)

        elif entity_type == 'mpaa':
            pg13 = re.match('[Pp][Gg]\s*[-]?\s*13', entity['entity'].lower())
            nc17 = re.match('[Nn][Cc]\s*[-]?\s*17', entity['entity'].lower())
            if pg13:
                input_mpaa = 'PG-13'
            elif nc17:
                input_mpaa = 'NC-17'
            input_mpaa = entity['entity'].upper()
            user_session.movie_preferences['mpaa'].append(input_mpaa)

    return is_answered


def parse_yes_no(luis_intent):
    """
    Using Luis to detect if user is saying Yes, No, or something unintelligeable
    :param luis_intent: luis_intent to_dict
    :return: Enum.LuisYesNo
    """
    try:
        print("parse yes no", luis_intent.get('intent'))
        intent = luis_intent.get('intent')
        return LuisYesNo(intent)
    except ValueError:
        return None


def _entity_type_from_luis_entity(luis_entity: str) -> Optional[str]:
    entity_map = {
        'Entertainment.ContentRating': 'mpaa',
        'Entertainment.Genre': 'genre',
        'Entertainment.Role': 'role',
        'Entertainment.Title': 'title',
        'Entertainment.UserRating': 'rating',
        'Entertainment.Person': 'person',
        'builtin.datetimeV2.duration': 'duration',
        'builtin.datetimeV2.daterange': 'year',
    }
    return entity_map.get(luis_entity)


def _luis_entity_from_state(state: str) -> Optional[str]:
    state_to_entity_map = {
        'genre': 'genre', 'role': 'role', 'mpaa': 'mpaa', 'title': 'title', 'rating': 'rating',
        'actor': 'person', 'director': 'person', 'year': 'year'
    }
    return state_to_entity_map.get(state)


def map_intent(state: str, intent, entities, user_cache):
    # from pprint import pprint
    # print()
    # pprint(intent)
    # print()
    # pprint(entities)
    # print()
    answered = True
    entity_map = {'Entertainment.ContentRating': 'mpaa', 'Entertainment.Genre': 'genre', 'Entertainment.Role': 'role',
                  'Entertainment.Title': 'title', 'Entertainment.UserRating': 'rating', 'Entertainment.Person':
                      'person', 'builtin.datetimeV2.duration': 'duration', 'builtin.datetimeV2.daterange': 'year',
                  }
    state2entity_map = {'genre': 'genre', 'role': 'role', 'mpaa': 'mpaa', 'title': 'title', 'rating': 'rating',
                        'actor': 'person', 'director': 'person', 'year': 'year'}

    # elif intent['intent']=='Year':
    #     #default by setting year to
    if intent['intent'] == 'NoPreference' or intent['intent'] == 'Yes' or intent['intent'] == 'No':
        answered = True
        user_cache['satisfied'] = intent['intent']
        return user_cache, answered

    for ent in entities:
        data_type = entity_map[ent['type']]
        if data_type != state2entity_map[state]:
            answered = False
            continue

        if data_type == 'year' or data_type == 'duration':
            # for now we will do nothing with year and duration
            user_cache[data_type] = year(ent)
        elif data_type == 'mpaa':
            pg13 = re.match('[Pp][Gg]\s*[-]?\s*13', ent['entity'].lower())
            nc17 = re.match('[Nn][Cc]\s*[-]?\s*17', ent['entity'].lower())
            if pg13:
                ent['entity'] = 'PG-13'
            elif nc17:
                ent['entity'] = 'NC-17'
            ent['entity'] = ent['entity'].upper()
        elif data_type == 'person':
            ent['entity'] = ent['entity'].title()
            # this is to create two categories one for actor and director instead of people
            data_type = state
        elif data_type == 'genre':
            print('genre_input: ' + ent['entity'])
            input_genre = genre_spellcheck(ent['entity'])
            print('genre_output: ' + input_genre)
            ent['entity'] = input_genre

        if user_cache[data_type]:
            if ent['entity'] not in user_cache[state]:
                user_cache[data_type].append(str(ent['entity']))
        else:
            user_cache[data_type] = [str(ent['entity'])]

        # if intent['intent'] == 'None':
        #     return userCache, answered

    print(user_cache)
    return user_cache, answered


# Implement scoring and this can be a follow up function that could be a series of binary questions.
def year(entity):
    return '2017'
