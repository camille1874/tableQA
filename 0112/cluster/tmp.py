import numpy as np
from sklearn.cluster import KMeans
import re
import os
import gzip
import collections

#lines = open("./WikiTableQuestions/data/random-split-1-train.examples").readlines()
lines = open("/home/xuzh/0112/data/WikiTableQuestions/data/training.examples").readlines()
#lgf_dir = "./lgfs_wo_conflict_new1/"
lgf_dir = "/home/xuzh/0112/data/lgfs_new/"
question_dic = {}
lgf_dic = {}
operators = ["filter_date_equals", "filter_date_not_equals", "filter_date_lesser_equals", "filter_date_greater_equals", "filter_date_lesser", "filter_date_greater", "filter_number_equals", "filter_number_not_equals", "filter_number_lesser_equals", "filter_number_greater_equals", "filter_number_lesser", "filter_number_greater", "filter_in", "filter_not_in", "select_string", "select_number", "select_date", "first", "last", "count", "argmin", "argmax", "min_date", "max_date", "max_number", "min_number", "sum", "average", "mode_string", "mode_number", "mode_date", "next", "previous", "same_as", "diff"]
# len=35
for l in lines:
    p = re.compile("utterance \"[^\"]*\"")
    ques = p.findall(l)[0].replace("utterance ", "").strip("\"")
    p = re.compile("id nt-\\d+")
    idx = p.findall(l)[0].replace("id nt-", "")
    question_dic[int(idx)] = ques

for lgf_path in os.listdir(lgf_dir):
    g_file = gzip.open(lgf_dir + lgf_path)
    raw_lgf = [lgf.strip().decode('utf-8') for lgf in g_file]
    lgf = raw_lgf[0]
    # 原先按嵌套层数排序了，暂时取第一个。可以按常见operator排个序来取。
    key = int(lgf_path.replace(".gz", "").replace("nt-", ""))
    if key in question_dic:
        lgf_dic[key] = lgf
    g_file.close()


lgf_dic = sorted(lgf_dic.items(), key = lambda i: i[0])
len1 = len(lgf_dic)
len2 = len(operators)
array = np.zeros((len1, len2))
for i in range(len(lgf_dic)):
    value = lgf_dic[i][1]
    for j in range(len(operators)):
        ope = operators[j]
        if ope in value:
            array[i][j] = 1

#print(array)

estimator = KMeans(n_clusters=15)
estimator.fit(array)
label_pred = estimator.labels_
#centroids = estimator.cluster_centers_
#inertia = estimator.inertia_

#print(label_pred)
classes = collections.defaultdict(list)
for i in range(len(label_pred)):
    key = lgf_dic[i][0]
    question = question_dic[key]
    lgf = lgf_dic[i][1]
    classes[label_pred[i]].append({key: (question, lgf)})

classes = sorted(classes.items(), key = lambda i: i[0])
for key, values in classes:
    print("#" * 50)
    print(key)
    for v in values:
        print(v)
