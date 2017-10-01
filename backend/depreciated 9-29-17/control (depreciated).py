#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import understand
import retrieval
import random
import sys
import sentiment_vader
import oov
import name_entity
import nltk
import rl_test


def Init():
    Tree = ConstructTree()
    Template = ConstructTemplate()
    return Tree, Template


def FindCandidate(model, database, resource, input_utter, history, tfidfmodel=None, tfidfdict=None):
    # print "In Control tfidfmodel: "
    # print tfidfmodel
    # print 'In Control tfidfdict '
    # print tfidfdict
    # word2vec = 0
    meta_info = ScoreInput(model, database, resource, input_utter, history, tfidfmodel, tfidfdict)
    # print ""
    #if the input utterance is empty
    if meta_info.__len__() == 0:
        relavance = 0
        answer = 'Can you say something longer.'.split(' ')
    else:
        #Candidates, TopicLevel = retrieval.FreqPairMatch(meta_info, database)
        #                print 'history'
        #                print history
        # print Candidates
        relavance, answer, tag = retrieval.Select(Candidates, history, model)
        # print "answer from ", tag
        # print 'Candidates[0][0]'
        # print Candidates[0][0]
        if Candidates:
            if relavance != Candidates[0][0]:
                word2vec = 1
    return relavance, answer


def ScoreInput(model, database, resource, input_utter, history, tfidfmodel=None, tfidfdict=None):
    # print "In Control tfidfmodel: "
    # print tfidfmodel
    # print 'In Control tfidfdict '
    # print tfidfdict
    # word2vec = 0
    if not tfidfmodel == None and not tfidfdict == None:
        meta_info = understand.InfoExtractor(input_utter, resource, history, tfidfmodel, tfidfdict)
    else:
        meta_info = understand.InfoExtractor(input_utter, resource, history)
    # print "Understand"
    return meta_info

# @based on response weight
def SelectState_rel_only(str_rule, relevance, user_input, pre_history, TreeState, dictionary_value,
                     q_table, TemplateLib, TopicLib,
                         Template):
    branch_idx = TreeState.keys()[0]
    branch = TreeState[branch_idx]['node']
    # print TreeState
    # print branch_idx
    # print branch
    if user_input in pre_history:
        return {'name': 'not_repeat'}, 'You already said that!'

    if relevance >= branch['threshold_relevance']:
        return TreeState[branch_idx][True][0], None
        # only use the continue, don't expand

    else:
        # if name_entity_mode is 1:
        #     name_entity_list = name_entity.name_entity_detection(user_input)
        #     if name_entity_list:
        #         name_entity_disp = name_entity.NE_kb(name_entity_list)
        #         if name_entity_disp:
        #             print 'name entity is triggerd'
        #             output_oov = name_entity.name_entity_generation(name_entity_list, name_entity_disp)
        #             # if output_oov != previous_history[user_id][-1]:
        #             return {'name': 'name_entity'}, output_oov, theme, init_id, joke_id, more_id
        #
        # if short_answer_mode is 1:
        #     if (user_input.find(' ') == -1):
        #         print 'it is a single word'
        #         word_list = nltk.word_tokenize(user_input)
        #         for word in word_list:
        #             if word not in dictionary_value:
        #                 # print 'user_input not in dictionary_value'
        #                 print 'short answer is triggered'
        #                 # strategy.append('short_answer')
        #                 output = 'Will you be serious, and say something in a complete sentence?'
        #                 return {'name': 'short_answer'}, output, theme, init_id, joke_id, more_id
        #
        # if oov_mode is 1:
        #     chosen, dictionary_value, output_oov = oov.oov_out(user_input, dictionary_value)
        #     if chosen is 1:
        #         print 'oov is triggerd'
        #         output = output_oov
        #         return {'name': 'oov'}, output_oov, theme, init_id, joke_id, more_id

        # if policy_mode == 0 or pre_history == None:
        #     return random.choice(TreeState[branch_idx][False][0:-1]), None, theme, init_id, joke_id, more_id
        # # don't choose the last leave, go back
        # curr_1 = sentiment_vader.get_sentiment(user_input)
        # curr_2 = sentiment_vader.get_sentiment(pre_history[-1])
        # curr_3 = sentiment_vader.get_sentiment(pre_history[-2])
        #
        # if policy_mode == 1 and pre_history is not None:
        #     strategy = str_rule[(curr_1, curr_2, curr_3)]
        #     return {'name': strategy}, None, theme, init_id, joke_id, more_id
        #
        # #reinforcement?
        # if policy_mode == 'rl':
        #     turn_id = len(pre_history) / 2
        #     if turn_id > 11:
        #         turn_id == 11
        #     theme_new, action, output, init_id, joke_id, more_id = rl_test.rl_test(curr_1, curr_2, curr_3, turn_id,
        #                                                                            q_table, theme, TemplateLib,
        #                                                                            TopicLib, Template, init_id, joke_id,
        #                                                                            more_id)
            #return {'name': action}, output

        return TreeState[branch_idx][False][1], None


def SelectState(relavance, engagement, TreeState, engaged_list):
    branch_idx = TreeState.keys()[0]
    branch = TreeState[branch_idx]['node']
    if engagement >= branch['threshold_engagement']:
        return random.choice(TreeState[branch_idx][True])
    elif (engagement < branch['threshold_engagement']) and (len(engaged_list) == 0):
        return random.choice(TreeState[branch_idx][False][
                             0:-1])  # random selection between the tree leaves,expcet the last leave, go back
    else:
        return random.choice(TreeState[branch_idx][False])


def SelectState_rel(relavance, engagement, TreeState, engaged_list):
    branch_idx = TreeState.keys()[0]
    branch = TreeState[branch_idx]['node']
    if relavance >= branch['threshold_relevance']:
        return random.choice(TreeState[branch_idx][True])
    elif (relavance < branch['threshold_relevance']) and (len(engaged_list) == 0):
        return random.choice(TreeState[branch_idx][False][
                             0:-1])  # random selection between the tree leaves,expcet the last leave, go back
    else:
        return random.choice(TreeState[branch_idx][False])


def ConstructTree():
    Tree = {}
    # changed threshold relevance here from 0.2 to 0.12
    branch = {'tag': 'criteria', 'name': 'relevance', 'threshold_relevance': 0.3, 'threshold_engagement': 3}
    switch_state = {'tag': 'state', 'name': 'switch'}
    end_state = {'tag': 'state', 'name': 'end'}
    init_state = {'tag': 'state', 'name': 'init'}  # initiate things to do
    joke_state = {'tag': 'state', 'name': 'joke'}  # tell a joke
    back_state = {'tag': 'state', 'name': 'back'}  # mention the high engagement point back in history
    continue_state = {'tag': 'state', 'name': 'continue'}
    expand_state = {'tag': 'state', 'name': 'expand'}
    more_state = {'tag': 'state', 'name': 'more'}
    oov_state = {'tag': 'state', 'name': 'oov'}
    name_entity_state = {'tag': 'state', 'name': 'name_entity'}
    short_answer = {'tag': 'state', 'name': 'short_answer'}
    not_repeat = {'tag': 'state', 'name': 'not_repeat'}
    Tree[0] = {'node': branch}
    Tree[0][True] = [continue_state, expand_state]
    Tree[0][False] = [switch_state, end_state, init_state, joke_state, more_state,
                      back_state]  # switch state here means strategy selection selection state.
    return Tree


# construct a tree based on confidence.
# def ConstructTemplate():
#        template = {}
#        template['switch'] = ['template_end', 'template_new,topic']
#        template['end'] = ['answer', 'template_open']
#        template['continue']=['answer']
#        template['expand'] = ['answer', 'template_expand']
#        return template#

# @zhou construct tree with strategy selection
def ConstructTemplate():
    template = {}
    template['switch'] = ['template_end', 'template_new,topic']
    template['init'] = ['template_init']
    template['end'] = ['template_end', 'template_open']
    template['continue'] = ['answer']
    template['expand'] = ['answer', 'template_expand']
    template['back'] = ['template_end', 'template_back,topic_back']
    template['more'] = ['template_more']
    template['joke'] = ['template_end', 'template_joke']
    template['oov'] = ['oov']
    template['short_answer'] = ['short_answer']
    template['name_entity'] = ['name_entity']
    template['not_repeat'] = ['not_repeat']
    return template
