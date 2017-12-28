#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import numpy as np

import candidates
import database_connect
import movieCtrl

cur = database_connect.db_connect()


def ctrl(cache_results, titles_user, scoreweights, history):
    output = []
    temp = ''
    for k, v in cache_results.iteritems():
        temp += k.title() + " : "
        if v:
            temp += ','.join(v).title() + " | \n "
        else:
            temp += 'No Preference' + " | \n "
            # qtup = ("Here is the information I have gathered in this conversation. " + temp, 'tell')
            # mscores, mmap = candidates.find(cache_results[userid])
    mscores, mmap = candidates.find(titles_user, cache_results)
    movieWithScore = sorted(zip(mmap, np.dot(mscores, scoreweights)), key=lambda tup: tup[1],
                        reverse=True)

    print
    print movieWithScore[:10]
    print
    # not sure why this occasionally excepts keyerror from movieWith Score
    if movieWithScore:
        data = movieCtrl.moviebyID(movieWithScore[0][0])
        print data
        # process directors and actors into readable for output
        output.append("How about " + data[1] + " (" + data[
            3] + ")? ")
        if len(data) > 10:
            dlist = data[12].split(' ')
            alist = data[14].split(' ')
            actorNameList = movieCtrl.actorsbyID(alist)
            directorNameList = movieCtrl.actorsbyID(dlist)
            output.append(data[1] + " stars " + ", ".join(actorNameList) + " and is directed by " + \
                          ", ".join(directorNameList) + ".")
        output.append("This film is {} minutes long. It is {} {} movie, and is rated {}.".format(
            data[8],
            "an" if any(v in data[4][:1].lower() for v in ['a','e','i','o','u']) else "a",
            data[4].replace(" ", ",", data[4].count(" ") - 1)\
                    .replace(" ", " and ")\
                    .replace(",", ", "),
            data[6]
        ))
    return output
