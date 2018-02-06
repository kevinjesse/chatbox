import pickle
#import matplotlib
import copy
import numpy as np
from scipy.sparse import coo_matrix
from scipy.io import mmwrite, mmread
#matplotlib.use('Agg')
#from matplotlib import pyplot as plt
import database_connect

cur = database_connect.db_connect()
netflix_set = {}
movie_names = set()
titles = set()
names = set()


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





net_titles = open("movie_titles.txt", "r")

for each in net_titles:
    movierow = each.split(',')
    movie_name = movierow[-1].strip()
    movie_id = movierow[0].strip()
    netflix_set[movie_name] = movie_id
    movie_names.add(movie_name)

both = list(set(movie_names).intersection(set(names)))

both = list(set(movie_names).intersection(set(names)))
sizeofboth = len(both)
user_set = dict()
print "HERE"
print both
for mov in both:
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

with open("user_set.txt", "wb") as fp:  # Pickling
    pickle.dump(user_set, fp)

# def getUserSet():
#     both = list(set(movie_names).intersection(set(names)))
#     sizeofboth = len(both)
#     user_set = dict()
#     for mov in both:
#         id = netflix_set[mov]
#         text_file = "mv_"+id.zfill(7)+".txt"
#         print text_file
#         with open("./training_set/" + text_file, "r") as f:
#             next(f)
#             for i, l in enumerate(f):
#                 userrow = l.split(',')
#                 user_id = userrow[0].strip()
#                 # print user_id
#                 # print user_list
#                 try:
#                     user_set[user_id] += 1
#                 except KeyError as e:
#                     user_set[user_id] = 1
#
#     with open("user_set.txt", "wb") as fp:   #Pickling
#          pickle.dump(user_set, fp)
#     return user_set, both
#



# with open("netflix_map.txt", 'wb') as f:
#     pickle.dump(netflix_set, f)
#
# for each in both:
#     #print str(k) + " : " +str(v)
#     id = netflix_set[each]
#     sqlstring = """UPDATE title SET netflixid='""" + id + """' WHERE primarytitle ='""" + each.replace("'","''") + """'"""
#     print sqlstring
#     cur.execute(sqlstring)
# exit()


bothdic = dict()
for movie_name in both:
    try:
        bothdic[movie_name] = netflix_set[movie_name]
    except KeyError:
        continue

#both = list(set(movie_names).intersection(set(names)))
#userlist = sorted(user_set.items(), key=lambda (k, v): v, reverse=True)[0:341]
userlist = sorted(user_set, key=user_set.get, reverse=True) #477396 users

movielist = sorted(bothdic.itervalues(), key=bothdic.get)
net_table = np.zeros((len(movielist),len(userlist)))

print "PROCESSING"
for mov in movielist:
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
                net_table[row][col] = user_rate
            except ValueError as e:
                continue

sparse = coo_matrix(net_table)
print sparse
mmwrite("sparse.mm", sparse)
try:
    with open("userlist.txt", 'wb') as f:
        pickle.dump(userlist, f)

    with open("movielist.txt", 'wb') as f:
        pickle.dump(movielist, f)

except IOError as e:
    exit(1)
exit(0)


#Does user_set need to be pushed?
try:
    with open("user_set.txt", "r") as fp:
        pass
except IOError as e:
    user_set = getUserSet()
    pass

# print bothdic
# print len(bothdic)

# sorted_user_set = sorted(user_set.items(), key=lambda (k, v): v, reverse=True)
# print sorted_user_set[0:340]

#sorted_user_values = sorted(user_set.itervalues(), reverse=True)

# number of reviews by user
# plt.plot(range(0,len(sorted_user_values[20:500])),sorted_user_values[20:500] )
# plt.title("How many reviews each user ranked")
# plt.ylabel('Number of reviews')
# plt.xlabel('Users')
# plt.savefig('plot.png')


# Looking at top 340 users
# Other option is between 900-800 reviews which is 277 users

# print len(user_set)
# print "********"
# count = 0
# for each in sorted(user_set.itervalues(), reverse=True):
#     if each >= 800:
#         count +=1
#
#         # print "#########"
#         # print each
#         # print "#########"
# print( "******** COUNT: " + str(count))

