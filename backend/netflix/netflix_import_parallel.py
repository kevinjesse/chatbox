import pickle
#import matplotlib
import copy
import numpy as np
from scipy.sparse import coo_matrix
from scipy.io import mmwrite, mmread
#matplotlib.use('Agg')
#from matplotlib import pyplot as plt
import database_connect

from collections import defaultdict



from joblib import Parallel, delayed
import multiprocessing

cur = database_connect.db_connect()
netflix_set = {}
movie_names = set()
titles = set()
names = set()

def userfreq(mov, netflix_set):
    user_set = dict()
    id = netflix_set[mov]
    text_file = "mv_" + id.zfill(7) + ".txt"
    print text_file
    with open("./training_set/" + text_file, "r") as f:
        next(f)
        for i, l in enumerate(f):
            userrow = l.split(',')
            user_id = userrow[0].strip()
            # print user_id
            # print user_list

            try:
                user_set[user_id] += 1
            except KeyError as e:
                user_set[user_id] = 1

    return user_set

def ratings(mov, userlist, movielist):
    #global net_table
    rows = []
    cols= []
    data = []
    # global net_table, userlist, movielist
    row = movielist.index(mov)
    text_file = "mv_" + mov.zfill(7) + ".txt"
    print text_file
    with open("./training_set/" + text_file, "r") as f:
        next(f)
        for i, l in enumerate(f):
            userrow = l.split(',')
            user_id = userrow[0].strip()
            #if user_id in userlist:
            try:
                col = userlist.index(user_id)
                user_rate = userrow[1].strip()
                #print "adding "+ user_rate +" at row " +str(row) + ", col " + str(col)
                rows.append(row)
                cols.append(col)
                data.append(user_rate)
                #print user_rate
                # net_table[row][col] = user_rate
            except ValueError as e:
                #print "value error"
                continue
   # return net_table
    return rows, cols, data
#-----------------------------------------------------------------------
# Stat Generation

#
#
# a= mmread("sparse.mm.mtx")
# c = 0
# small = 999999
# large = 0
# temp = 0
# for i,j,v in zip(a.row, a.col, a.data):
#
#     print i
#     if i == c:
#         print "match"
#         temp +=1
#     else:
#         temp+=1
#         if temp>large: large = temp
#         if temp<small: small = temp
#         temp = 0
#         c+=1
#         if i != c:
#             print "ERROR"
#             print "c"
#             exit(1)
# print "OK"
# print small
# print large
# exit(0)
#
#
#
#
#------------------------------------------------------------------------





try:
    # with open("user_set.txt", "r") as fp:
    #     user_set = pickle.load(fp)
    with open("titles.txt", "rb") as fp:  # Unpickling
        titles = pickle.load(fp)
    with open("names.txt", "rb") as fp:  # Unpickling
        names = pickle.load(fp)

except IOError as e:
    # ------------------------------------------------------------------------
    #If titles.txt and names.txt do not exist

    sqlstring = """SELECT tconst, primarytitle FROM title"""
    cur.execute(sqlstring)
    rows = cur.fetchall()
    for mov in rows:
        titles.add(mov[0])
        names.add(mov[1])
    # titles.append()
    # names.append()

    with open("titles.txt", "wb") as fp:   #Pickling
        pickle.dump(titles, fp)

    with open("names.txt", "wb") as fp:   #Pickling
        pickle.dump(names, fp)

    #getUserSet()
    # -----------------------------------------------------------------------
    exit(-1)



num_cores = multiprocessing.cpu_count()

net_titles = open("movie_titles.txt", "r")

for each in net_titles:
    movierow = each.split(',')
    movie_name = movierow[-1].strip()
    movie_id = movierow[0].strip()
    netflix_set[movie_name] = movie_id
    movie_names.add(movie_name)

both = list(set(movie_names).intersection(set(names)))
sizeofboth = len(both)

user_set_p = Parallel(n_jobs=num_cores)(delayed(userfreq)(mov, netflix_set) for mov in both)

#reduce
user_set_temp = defaultdict(list)
for d in user_set_p: # you can list as many input dicts as you want here
    for key, value in d.iteritems():
        user_set_temp[key].append(value)

users_freq = dict()
for k,v in user_set_temp.iteritems():
    users_freq[k] = sum(v)

user_set = users_freq

bothdic = dict()
for movie_name in both:
    try:
        bothdic[movie_name] = netflix_set[movie_name]
    except KeyError:
        continue

userlist = sorted(user_set.items(), key=lambda (k, v): v, reverse=True)[0:5000]
#userlist = sorted(user_set.items(), key=lambda (k, v): v, reverse=True)[0:200000]

movielist = sorted(bothdic.itervalues(), key=bothdic.get)
net_table = np.zeros((len(movielist),len(userlist)))

userlist = [i[0] for i in userlist]

coo = Parallel(n_jobs=num_cores)(delayed(ratings)(mov, userlist, movielist) for mov in movielist)
coo_rows = []
coo_cols = []
coo_data = []
for a_set in coo:
    coo_rows.extend(a_set[0])
    coo_cols.extend(a_set[1])
    coo_data.extend(a_set[2])

# print len(coo_rows)
# print len(coo_cols)
for idx in range(0,len(coo_rows)):
    row = coo_rows[idx]
    col = coo_cols[idx]
    data = coo_data[idx]
    net_table[row][col] = data

sparse = coo_matrix(net_table)

mmwrite("sparseNp.mm", sparse)
try:
    with open("userlist.txt", 'wb') as f:
        pickle.dump(userlist, f)

    with open("movielist.txt", 'wb') as f:
        pickle.dump(movielist, f)

except IOError as e:
    exit(1)
exit(0)


