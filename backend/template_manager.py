# Austin Chau
# @author amchau@ucdavis.edu
#

import random
import yaml
from enum import Enum
from typing import Optional

ymlpath = 'resource/template/template.yml'

yml: dict = None


def init_resources():
    global yml
    try:
        f = open(ymlpath, 'r')
        yml = yaml.load(f)
    except yaml.YAMLError as e:
        raise e


def get_sentence(dialogue_type: str,
                 state: str=None,
                 options: str=None,
                 returning_count: int=0,
                 return_all=False):

    utterance = yml[dialogue_type]

    if state is not None:
        utterance = utterance[state]

    if options is not None:
        utterance = utterance[options]

    if type(utterance) is dict:
        utterance = utterance[returning_count]

    return random.choice(utterance) if not return_all else utterance







# def get_sentence(state: State, is_dynamic: bool=False, replacement=None) -> str:
#     """
#     The method that generates a sentence from the template for the AI to speak.
#     :type state: string. NOTE: please use the class State for consistency.
#     :type is_dynamic: bool
#     :type replacement: [string]
#     :param state: the current question state. e.g. genre, actor
#     :param is_dynamic: whether to use strings that have replaceable placeholders.
#     :param replacement: list of items to be used for replacement.
#     :return: a final string that can be output by AI.
#     """
#     # TODO: gracefully decline request for dynamic sentences when there is none in template.
#     is_dynamic_string = "dynamic" if is_dynamic else "static"
#
#     elem_questions = list(xml.iterfind(
#         "state[@type='{}']/{}/question_group[@type='root']/".format(
#             state.value, is_dynamic_string
#         )))
#
#     return __get_question_string(elem_questions, is_dynamic, replacement)
#
#
# def get_followup(question_tag, state, is_dynamic, replacement=None):
#     is_dynamic_string = "dynamic" if is_dynamic else "static"
#
#     elem_questions = list(xml.iterfind(
#         "state[@type='{}']/{}/question_group[@type='follow_up']/*[@tag='{}']".format(
#             state, is_dynamic_string, question_tag
#         )))
#
#     return __get_question_string(elem_questions, is_dynamic, replacement)
#
#
# def __get_question_string(xml_element, is_dynamic, replacement):
#     """
#     The internal method that takes in a question_group element,
#     choose a question in random and return a formatted string.
#     :param xml_element: the xml element corresponding to the selected question_group.
#     :param is_dynamic: whether to use strings that have replaceable placeholders.
#     :param replacement: list of items to be used for replacement.
#     :return: a formatted string ready for output
#     """
#     if len(xml_element) != 0:  # in case xml return None
#         if is_dynamic and replacement is not None:
#             elem_question = random.choice(filter(
#                 lambda x:
#                 int(x.find('choice_count').text) == -1 or int(x.find('choice_count').text) == len(
#                     replacement),
#                 xml_element))
#             return __format_dynamic_template(elem_question, replacement)
#         else:
#             elem_question = random.choice(xml_element)
#             return elem_question.find('string').text
#     else:
#         print("elem_questions has 0 length")
#
#
# def __format_dynamic_template(xml_element, replacement):
#     """
#     Internal method for string interpolation for replaceable string in template.
#     :param xml_element: the xml element corresponding to <question>
#     :param replacement: list of strings to be used for replacement
#     :return: a formatted, replaced string.
#     """
#     try:
#         num_replacement = int(xml_element.find('choice_count').text)
#     except ValueError:
#         print(ValueError)
#         return xml_element.find('string').text
#
#     question_string = xml_element.find('string').text
#
#     # TODO: Support replacement of multiple match_strings
#     match_strings_raw = xml_element.find('replacements').find('string')
#     match_string = "$({})".format(match_strings_raw.text)
#
#     if num_replacement == -1:
#         match_string_variable = "$({}...)".format(match_strings_raw.text)
#         r_string_composed = ", ".join(replacement[:-1])
#
#         question_string = question_string.replace(match_string_variable, r_string_composed, 1)
#         question_string = question_string.replace(match_string, replacement[-1], 1)
#         return question_string
#     else:
#         for i in range(min(num_replacement, len(replacement))):
#             question_string = question_string.replace(match_string, replacement[i], 1)
#         return question_string
