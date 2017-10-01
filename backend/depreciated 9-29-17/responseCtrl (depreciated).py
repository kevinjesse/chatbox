#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

def responseBinSim(input):
    """
    :param input: user input
    :return: score as yes or no. still need to work on gensim comparisons
    """
    yeslist = ['yes', 'yep', 'yup', 'ok', 'okay', 'yea', 'yeah', 'sure', 'ya']
    nolist = ['no', 'nope', 'no way', 'not at all', 'nay', 'negative']
    input = input.lower()
    if any(match in input for match in yeslist):
        return True
    if any(match in input for match in nolist):
        return False