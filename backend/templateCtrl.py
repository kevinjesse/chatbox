# Austin Chau
# @author amchau@ucdavis.edu
#

from xml.etree import cElementTree
import random

xmlpath = "resource/template/template.xml"


class State:
    MOVIE = 'movies'
    GENRE = 'genre'
    ACTOR = 'actor'
    DIRECTOR = 'director'
    MPAA = 'mpaa'
    RATING = 'rating'
    TELL = 'tell'
    TELL1 = 'tell1'
    TELL1_5 = 'tell1_5'
    TELL2 = 'tell2'
    BYE = 'bye'


def init_resources():
    """
    Call this method to initialize the xml load.
    IMPORTANT: XML needs to be loaded or error ensues.
    :return: void
    """
    global xml
    xml = cElementTree.parse(xmlpath).getroot()


def get_sentence(state, is_dynamic, replacement=None):
    """
    The method that generates a sentence from the template for the AI to speak.
    :type state: string. NOTE: please use the class State for consistency.
    :type is_dynamic: bool
    :type replacement: [string]
    :param state: the current question state. e.g. genre, actor
    :param is_dynamic: whether to use strings that have replaceable placeholders.
    :param replacement: list of items to be used for replacement.
    :return: a final string that can be output by AI.
    """
    # TODO: gracefully decline request for dynamic sentences when there is none in template.
    is_dynamic_string = "dynamic" if is_dynamic else "static"

    elem_questions = list(xml.iterfind(
        "state[@type='{}']/{}/question_group[@type='root']/".format(
            state, is_dynamic_string
        )))

    return __get_question_string(elem_questions, is_dynamic, replacement)


def get_followup(question_tag, state, is_dynamic, replacement=None):
    is_dynamic_string = "dynamic" if is_dynamic else "static"

    elem_questions = list(xml.iterfind(
        "state[@type='{}']/{}/question_group[@type='follow_up']/*[@tag='{}']".format(
            state, is_dynamic_string, question_tag
        )))

    return __get_question_string(elem_questions, is_dynamic, replacement)


def __get_question_string(xml_element, is_dynamic, replacement):
    """
    The internal method that takes in a question_group element,
    choose a question in random and return a formatted string.
    :param xml_element: the xml element corresponding to the selected question_group.
    :param is_dynamic: whether to use strings that have replaceable placeholders.
    :param replacement: list of items to be used for replacement.
    :return: a formatted string ready for output
    """
    if len(xml_element) != 0:  # in case xml return None
        if is_dynamic and replacement is not None:
            elem_question = random.choice(filter(
                lambda x:
                int(x.find('choice_count').text) == -1 or int(x.find('choice_count').text) == len(
                    replacement),
                xml_element))
            return __format_dynamic_template(elem_question, replacement)
        else:
            elem_question = random.choice(xml_element)
            return elem_question.find('string').text
    else:
        print("elem_questions has 0 length")


def __format_dynamic_template(xml_element, replacement):
    """
    Internal method for string interpolation for replaceable string in template.
    :param xml_element: the xml element corresponding to <question>
    :param replacement: list of strings to be used for replacement
    :return: a formatted, replaced string.
    """
    try:
        num_replacement = int(xml_element.find('choice_count').text)
    except ValueError:
        print(ValueError)
        return xml_element.find('string').text

    question_string = xml_element.find('string').text

    # TODO: Support replacement of multiple match_strings
    match_strings_raw = xml_element.find('replacements').find('string')
    match_string = "$({})".format(match_strings_raw.text)

    if num_replacement == -1:
        match_string_variable = "$({}...)".format(match_strings_raw.text)
        r_string_composed = ", ".join(replacement[:-1])

        question_string = question_string.replace(match_string_variable, r_string_composed, 1)
        question_string = question_string.replace(match_string, replacement[-1], 1)
        return question_string
    else:
        for i in range(min(num_replacement, len(replacement))):
            question_string = question_string.replace(match_string, replacement[i], 1)
        return question_string
