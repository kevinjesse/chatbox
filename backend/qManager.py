

def output_sentence(using_choice = False, replacement = None, q_from_template):
    qtup = q_from_template #(question, tag)
    question = qtup[0]
    count = question.count(match)

    for i in range(count):
        question = question.replace(match, replace[i], 1)

    print
    question
