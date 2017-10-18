import random


# MARK: - Properties for this module

# MARK: - Public Methods

def output_sentence(using_choice, replacement, q_lib):
    """
    takes in parameters from dialogCtrl and manage the output of questions.
    :param using_choice: switch between old question template or the new Prefer A or B template
    :param replacement: the item to substitute A or B or ... with. Can be none if not using_choice
    :param q_lib: the global qLib is being passed as param here as the function needs it
    :return: return the qtup tuple in the format of (question_from_template or parsed A or B question, tag_from_template)
    """

    # return if not using choice or if replacement is None
    if not using_choice or replacement is None:
        return random.choice(filter(lambda x: x[1] == "choice", q_lib['choice']))  # (question, tag)

    # get a random question from template

    def q_lib_filter(q_lib_tuple):
        return q_lib_tuple[1] == "choice" and (q_lib_tuple[2] == len(replacement) or q_lib_tuple[2] == str(-1))

    question, tag, argc = random.choice(filter(q_lib_filter, q_lib["choice"]))

    # replacement

    question = __format_replaceable_q_lib_question(question, argc, replacement)

    # return
    return tuple((question, tag))


def __format_replaceable_q_lib_question(question_string, argc, replacement):
    """
    private method that replace $(state) from questions in q_lib
    :param question_string: the string question to be formatted
    :param argc: the argc returned from q_lib_template
    :param replacement: the array of replacement strings to be used for replacement
    :return: a string of formatted question
    """

    if argc == str(-1):  # argc == -1 means question has variable placeholders (e.g. $(state...))
        match_string = "$(choice)"
        match_string_variable = "$(choice...)"
        r_string_composed = ", ".join(replacement[:-1])
        question_string = question_string.replace(match_string_variable, r_string_composed, 1)
        question_string = question_string.replace(match_string, replacement[-1], 1)
        return question_string
    else:
        match_string = "$(choice)"
        for i in range(min(argc, len(replacement))):
            question_string = question_string.replace(match_string, replacement[i], 1)
        return question_string
