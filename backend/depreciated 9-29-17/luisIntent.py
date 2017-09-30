#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

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

    # elif intent['intent']=='Year':
    #     #default by setting year to
    if intent['intent'] == 'NoPreference' or intent['intent'] == 'Yes' or intent['intent'] == 'No':
        answered = True
        return userCache, answered
    
    for ent in entities:
        print "ENTITY NEXT "
        print ent['entity']
        dataType = entity_map[ent['type']]
        if dataType == state2entity_map[state]: answered = True
        if dataType == 'year' or dataType == 'duration':
            #for now we will do nothing with year and duration
            userCache[dataType] = year(ent)
        elif dataType == 'mpaa':
            pg13 = re.match('pg(-|\s?)13', ent['entity'].lower())
            nc17 = re.match('nc(-|\s?)17', ent['entity'].lower())
            if pg13: ent['entity']='PG-13'
            elif nc17: ent['entity']='NC-17'
        elif dataType =='person':
            ent['entity'] = ent['entity'].title()

        if userCache[dataType]:
            if ent['entity'] not in userCache[entity_map[ent['type']]]:
                userCache[dataType].append(ent['entity'])
        else:
            userCache[dataType] = [ent['entity']]

        # if intent['intent'] == 'None':
        #     return userCache, answered


    return userCache, answered

#Implement scoring and this can be a follow up function that could be a series of binary questions.
def year(entity):
    return '2017'