import codecs
import collections
import re
f = codecs.open("log_cluster.txt", encoding="utf-8")
lines = f.readlines()
classes = collections.defaultdict(dict)
ques_classes = {}
for i in range(len(lines)):
    if "###" in lines[i]:
        key = lines[i + 1].strip()
        continue
    if "{" in lines[i]:
        raw_id = lines[i].split(":")[0][1:]
        #ques = lines[i].split(",")[0].split("(")[1][1:-1]
        ques_classes[raw_id] = key
        lgf = lines[i].split(",")[1].strip()[1:-3]
        for l in lgf.split():
            if "(" in l:
                ope = l.replace("(", "")
                if ope in classes[key]:
                    classes[key][ope] += 1
                else:
                    classes[key][ope] = 1


ope_counts = classes
for key, value in classes.items():
    #print("#" * 50)
    #print("class: " + key)
    value = sorted(value.items(), key=lambda k:k[1], reverse=True)
    for k, v in value:
        #print(k)
        #print(v)
        if v < 20:
            ope_counts[key].pop(k)
for k, v in ope_counts.items():
    print(k)
    print(v)
