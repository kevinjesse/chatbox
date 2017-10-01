#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import nltk

from collections import defaultdict

from gensim import models, corpora

def AddWeight(tag_list, rules, stop_dict, tfidfvalues=None):
    result = []
    # print str(tag_list)
    #        if not tfidfvalues == None:
    #            for k in tfidfvalues.keys():
    #                print k, tfidfvalues[k]
    #        else:
    #            print "tfidf is not active"
    for token, pos in tag_list:
        if rules[pos] > 0:
            if not tfidfvalues == None:
                if token.lower() in tfidfvalues.keys():
                    result += [(token, pos, rules[pos] * tfidfvalues[token.lower()])]
                else:
                    result += [(token, pos, rules[pos])]
            else:
                result += [(token, pos, rules[pos])]
        else:
            if pos == ".":
                continue
            if not stop_dict[token]:
                result += [(token.lower(), pos, .1)]

                # for item in result:
                #   print item

    return result


# return [(token, pos_tag, weight)]
def InfoExtractor(utter, resource, history, tfidfmodel=None, tfidfdict=None):
    rules = resource['rules']
    stop_dict = resource['stop_words']
    tag_list = nltk.pos_tag(nltk.word_tokenize(utter))
    # if there is a pronoun in the last word of the sentence, we will look into previous history of TickTock output
    if not tfidfmodel == None and not tfidfdict == None:
        token = nltk.word_tokenize(utter)
        noun_list = []

        ##Currently unsure if I should have this for movies. Most likely NOT!
        for tag in tag_list:
            if tag[1] in ['PRP', 'PRP$'] and (tag[0].lower() not in ['you', 'i', 'we', 'my', 'me', 'yours', 'our']):
                # print tag
                if history:

                    # This is getting the noun list from the previous statement (AI)
                    TickTock_previous = history[-1]
                    tag_list_previous = nltk.pos_tag(nltk.word_tokenize(TickTock_previous))
                    noun_list = [item for item in tag_list_previous if item[1] in ['NN', 'NNS', 'NNP', 'NNPS']]
                    # print 'this is noun list'
                    # print noun_list
        if noun_list:
            # tag_list.append(noun_list[-1])
            token.append(noun_list[-1][0].lower())

        ##

        valList = tfidfmodel[tfidfdict.doc2bow(token)]
        # valList = tfidfmodel[tfidfdict.doc2bow(utter.lower().split())] ## talk to Neil about should we use word_tokenize?
        #                print "printing valList..."
        resDict = {}

        for tup in valList:
            key, score = tup
            dictKey = tfidfdict.get(key)
            if not dictKey == None:
                resDict[dictKey] = score
        # print 'anaphora trigger'
        # print anaphora_trigger

        print resDict
        return AddWeight(tag_list, rules, stop_dict, resDict)
    return AddWeight(tag_list, rules, stop_dict)
