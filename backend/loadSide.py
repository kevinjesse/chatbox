import pickle



def loadSide():
    try:
        # with open("user_set.txt", "r") as fp:
        #     user_set = pickle.load(fp)
        with open("userSideDict.txt", "rb") as fp:  # Unpickling
            full_user = pickle.load(fp)

    except IOError as e:
        print ("Cannot load files")
        exit(1)
    userSideReduce = dict()
    #We loaded our userSideDict but we need to filter out our irrelevant side data
    count = 0
    for user, user_val in full_user.iteritems():
        count += 1
        print count
        for sideType, freqDict in user_val.iteritems():
            top5 = sorted(freqDict, key=freqDict.get, reverse=True)[:5]
            full_user[user][sideType] = top5

    return full_user

userSideTop5 = loadSide()

try:
    import json
    with open("userSideTop5.txt", 'wb') as f:
        pickle.dump(userSideTop5, f)
        #json.dump(userSideTop5, f)

except IOError as e:
    print ("Cannot write files")
    exit(1)