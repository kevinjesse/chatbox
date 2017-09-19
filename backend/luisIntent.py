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



def ctrl(state, intent, entities, userCache):
    from pprint import pprint
    pprint(intent)
    pprint(entities)
    print
    print
    answered = False
    entity_map = {'Entertainment.ContentRating': 'mpaa', 'Entertainment.Genre': 'genre', 'Entertainment.Role': 'role',
                  'Entertainment.Title':'title', 'Entertainment.UserRating':'rating', 'Entertainment.Person': 'person',
                  'builtin.datetimeV2.duration': 'duration', 'builtin.datetimeV2.daterange': 'year',
                  }
    state2entity_map ={'genre': 'genre', 'role': 'role', 'mpaa':'mpaa', 'title': 'title', 'rating': 'rating',
                       'actor':'person', 'director': 'person', 'year': 'year'}
    if intent['intent'] == 'None':
        return userCache, answered
    elif intent['intent']=='NoPreference':
        answered = True
        return userCache, answered
    # elif intent['intent']=='Year':
    #     #default by setting year to

    for ent in entities:
        dataType = entity_map[ent['type']]
        if dataType == state2entity_map[state]: answered = True
        if dataType == 'year' or dataType == 'duration':

            userCache[dataType] = year(ent)
        else:
            if userCache[dataType]:
                if ent['entity'] not in userCache[entity_map[ent['type']]]:
                    userCache[dataType].append(ent['entity'])
            else:
                userCache[dataType] = [ent['entity']]

    return userCache, answered

#Implement scoring and this can be a follow up function that could be a series of binary questions.
def year(entity):
    return '2017'