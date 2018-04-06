#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

"""
Luis intent assigns the entities to the user cache and processes the intents
"""

#
# def genre(intent,entities, userCache):
#     if intent['intent'] == "goodGenre":
#         if userCache['genre']:
#             userCache['genre'] = userCache['genre'] + list(set(ent['entity'] for ent in entities) - set(userCache['genre']))
#         else:
#             userCache['genre'] = list(ent['entity'] for ent in entities)
#
#
#     return userCache

import re

from nltk.stem.snowball import SnowballStemmer


def genre_spellcheck(user_input):
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
        parsedinput = stemmer.stem(user_input)[:5]
        output = genre_stem[parsedinput] if parsedinput in genre_stem else user_input
        return output


def map_intent(state: str, intent, entities, user_cache):
    from pprint import pprint
    print()
    pprint(intent)
    print()
    pprint(entities)
    print()
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
        dataType = entity_map[ent['type']]
        if dataType != state2entity_map[state]:
            answered = False
            continue

        if dataType == 'year' or dataType == 'duration':
            #for now we will do nothing with year and duration
            user_cache[dataType] = year(ent)
        elif dataType == 'mpaa':
            pg13 = re.match('[Pp][Gg]\s*[-]?\s*13', ent['entity'].lower())
            nc17 = re.match('[Nn][Cc]\s*[-]?\s*17', ent['entity'].lower())
            if pg13: ent['entity']='PG-13'
            elif nc17: ent['entity']='NC-17'
            ent['entity'] = ent['entity'].upper()
        elif dataType =='person':
            ent['entity'] = ent['entity'].title()
            # this is to create two categories one for actor and director instead of people
            dataType = state
        elif dataType == 'genre':
            print('genre_input: ' + ent['entity'])
            input_genre = genre_spellcheck(ent['entity'])
            print('genre_output: ' + input_genre)
            ent['entity'] = input_genre

        if user_cache[dataType]:
            if ent['entity'] not in user_cache[state]:
                user_cache[dataType].append(str(ent['entity']))
        else:
            user_cache[dataType] = [str(ent['entity'])]

        # if intent['intent'] == 'None':
        #     return userCache, answered

    print(user_cache)
    return user_cache, answered

#Implement scoring and this can be a follow up function that could be a series of binary questions.
def year(entity):
    return '2017'