
from collections import defaultdict



from joblib import Parallel, delayed
import multiprocessing


netflix_set = {}
movie_names = set()
titles = set()
names = set()


def ratings(mov):
    movies = []
    text_file = "mv_" + mov.zfill(7) + ".txt"
    print text_file
    with open("./training_set/" + text_file, "r") as f:
        next(f)
        for i, l in enumerate(f):
            userrow = l.split(',')
            user_id = userrow[0].strip()
            user_rate = userrow[1].strip()
            #if user_id in userlist:
            try:
                movies.append({"ratingid": str(mov.zfill(7)) + str(user_id),
                               "movieid": str(mov.zfill(7)),
                               "userid": str(user_id),
                               "rating": user_rate})
            except ValueError as e:
                continue
    return movies

num_cores = multiprocessing.cpu_count()
net = open("movie_titles.txt", "r")

movies_p = Parallel(n_jobs=num_cores)(delayed(ratings)(mov) for mov in net)



import json
with open('netflix_json.txt', 'w') as outfile:
    json.dump(movies_p, outfile)



