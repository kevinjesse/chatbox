# Austin Chau
# @author amchau@ucdavis.edu
#

import random
import yaml
from enum import Enum
from typing import Optional

yml_path = 'resource/template/template.yml'

yml = None


def init_resources():
    global yml
    try:
        f = open(yml_path, 'r')
        yml = yaml.load(f)
    except yaml.YAMLError as e:
        raise e


def get_sentence(dialogue_type: str,
                 state: str=None,
                 options: str=None,
                 returning_count: int=0,
                 return_all=False):
    """
    Read template.yml to get a random sentences based on the input param
    :param dialogue_type: see yml
    :param state:
    :param options:
    :param returning_count:
    :param return_all:
    :return:
    """

    print(dialogue_type, state, options, returning_count, return_all)

    utterance = yml[dialogue_type]

    if state is not None:
        utterance = utterance[state]

    if options is not None:
        print(options, utterance)
        utterance = utterance[options]

    if type(utterance) is dict:
        print(utterance)
        utterance = utterance[returning_count]

    return random.choice(utterance) if not return_all else utterance

