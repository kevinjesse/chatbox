#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import nltk
from collections import defaultdict
import json
import os.path as path

#old default weights nounw=.8, adjw=1, numw=.8, verbbw=.6, verbw=.2, pverbw=.2,whw=.1
def LoadLanguageResource(nounw=.8, adjw=1, numw=.8, verbbw=.6, verbw=.2, pverbw=.2,whw=.1):
    WeightRules = defaultdict(int)
    # nounlist = ['NN', 'NNS', 'NNP', 'NNPS','PRP']
    # verblist = ['VBP','VB','VBG','VBZ']
    # whlist = ['WDT','WP','WP$','WRB']
    nounlist = ['NN', 'NNS', 'NNP', 'NNPS']
    adjlist = ['JJ', 'JJR', 'JJS', 'RP']
    verbbaselist = ['VB', 'VBN']
    verblist = ['VBP','VBG', 'VBZ']
    pastverblist = ['VBN', 'VBD']
    whlist = ['WDT', 'WP', 'WP$', 'WRB']
    numlist = ['CD']
    for noun in nounlist:
        WeightRules[noun] = nounw
    for adj in adjlist:
        WeightRules[adj] = adjw
    for num in numlist:
        WeightRules[num] = numw
    for verb in verbbaselist:
        WeightRules[verb] = verbbw
    for verb in verblist:
        WeightRules[verb] = verbw
    for verb in pastverblist:
        WeightRules[verb] = pverbw
    for wh in whlist:
        WeightRules[wh] = whw
    # WeightRules['VBP','VB','VBG','VBZ','VBN','WDT','WP','WP$','WRB'] = 1
    stop_dict = defaultdict(bool)
    for word in nltk.corpus.stopwords.words('english'):
        stop_dict[word] = True
    resource = {}
    resource['rules'] = WeightRules
    resource['stop_words'] = stop_dict
    return resource


def LoadData(datalist):
    database = {}
    for datafile in datalist:
        f = open(datafile)
        line = f.readline()
        f.close()
        raw_data = json.loads(str(line.strip()))
        database = PushData(raw_data, database)
    return database


def PushData(data, database):
    last = len(database.keys())
    for pair in data:
        database[last] = nltk.word_tokenize(pair['question'])
        last += 1
        database[last] = nltk.word_tokenize(pair['answer'])
        last += 1
    return database


def LoadDataPair(datalist):
    database = {}
    database['Q'] = {}
    database['A'] = {}

    # print datalist
    for datafile in datalist:
        f = open(datafile)
        # line = f.readline()
        line = f.read()
        f.close()
        # print (line)

        # print (str(line.strip()))
        # print line
        raw_data = json.loads(str(line.strip()))
        database = PushDataPair(raw_data, database)
    return database


def PushDataPair(data, database):
    last = len(database['Q'].keys())
    for pair in data:
        database['Q'][last] = nltk.word_tokenize(pair['question'])
        database['A'][last] = nltk.word_tokenize(pair['answer'])
        last += 1
    return database


def LoadTemplate(filelist):
    Library = {}
    for filepath in filelist:
        name = path.splitext(path.basename(filepath))[0]
        if name in ['template_init', 'template_joke']:
            Library[name] = {}
            for line in open(filepath):
                # print line
                theme, line_real = line.strip().split(';')  # i think you want to split then strip...
                # print theme
                try:
                    Library[name][theme].append(line_real)
                except KeyError:
                    Library[name][theme] = []
                    Library[name][theme].append(line_real)
        else:
            Library[name] = [line.strip() for line in open(filepath)]
    return Library


def LoadTopic(topicfile):
    return [line.strip() for line in open(topicfile)]


def LoadQuestions(question_file):
    qLib = []
    for line in open(question_file):
        a, q = line.split(';')
        a = a.strip()
        q = q.strip()
        qLib.append(tuple((q, a)))
        # try:
        #     qLib.append(tuple((q, a)))
        # except KeyError:
        #     qLib[q] = []
        #     qLib[type].append(q)
    return qLib


def LoadContinue(question_file):
    cLib = []
    for line in open(question_file):
        c, a, q = line.split(';')
        c = c.strip()
        a = a.strip()
        q = q.strip()
        cLib.append(tuple((q, a, c)))
        # try:
        #     qLib.append(tuple((q, a)))
        # except KeyError:
        #     qLib[q] = []
        #     qLib[type].append(q)
    return cLib