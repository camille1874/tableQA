import gzip
import os
import re
import collections
import codecs

#f = codecs.open("log_cluster.txt", encoding="utf-8")
f = codecs.open("log_cluster_all.txt", encoding="utf-8")
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
        if v < 10:
            ope_counts[key].pop(k)


filter_lst = ["first", "last", "argmax", "argmin", "count", "max_number", "min_number", "max_date", "min_date", "sum", "average", "mode_string", "mode_number", "mode_date", "next", "previous"]
replace_lst = ["first (first", "first (last", "last (first", "last (last", "argmax (argmax", "argmax (argmin", "argmin (argmin", "argmin (argmax"]
lgs_dir = "/home/geshi/nsm_allen/searched_lfs_with_rules_no_conservative/"
#new_dir = "/home/geshi/nsm_allen/lgfs_wo_conflict_new1/"
new_dir = "/home/geshi/nsm_allen/lgfs_new_class/"

coved = 0

for lgs_path in os.listdir(lgs_dir):
    #if lgs_path != "nt-6510.gz":
    #    continue
    g_file = gzip.open(lgs_dir + lgs_path)
    final_lgf = []

    raw_lgf = [lgf.strip().decode('utf-8') for lgf in g_file]
    #new_lgf = []
    new_lgf = raw_lgf
    print(lgs_path)
    print("raw_lgf" + "#" * 50)

    for r in raw_lgf:
        print(r)


    ##print("replace filter:" + "*" * 50)
    #for r in raw_lgf:
    #    for l in replace_lst:
    #        if l in r:
    #            idx = r.split("(").index(l.split("(")[0])
    #            tmp = r.split("(")
    #            tmp.pop(idx)
    #            r = "(".join(tmp)
    #            tmp = r.split(")")
    #            tmp.pop(-idx - 1)
    #            r = ")".join(tmp)
    #    new_lgf.append(r)
    ##for r in new_lgf:
    ##    if r not in raw_lgf:
    ##        print(r)


    #print("replace filter 1:" + "*" * 50)
    #raw_lgf = new_lgf
    #new_lgf = []
    #for r in raw_lgf:
    #    if "(previous (next" in r:
    #        targ = "(previous (next"
    #        p = " \\(previous \\(next[^\\(\\)]*\\)\\)"
    #    elif "(next (previous" in r:
    #        targ = "(next (previous"
    #        p = " \\(next \\(previous[^\\(\\)]*\\)\\)"
    #    else:
    #        if len(r.split()) > 1:
    #            new_lgf.append(r)
    #        continue
    #    if re.findall(p, r):
    #        r = re.sub(p, "", r)
    #    else:
    #        idx = len(r[:r.find(targ)].split("("))
    #        tmp = r.split("(")
    #        tmp.pop(idx)
    #        tmp.pop(idx)
    #        res = "(".join(tmp)
    #        tmp = res.split(")")
    #        tmp.pop(-idx - 1)
    #        tmp.pop(-idx - 1)
    #        r = ")".join(tmp)
    #        if len(r.split()) > 1:
    #            new_lgf.append(r)

    #for r in new_lgf:
    #    if r not in raw_lgf:
    #        print(r)


    #print("same_as filter:" + "*" * 50)
    filter_in = [lgf for lgf in raw_lgf if "filter" in lgf and "same_as" not in lgf]
    if filter_in:
        new_lgf = [lgf for lgf in raw_lgf if "same_as" not in lgf]
    #for r in raw_lgf:
    #    if r not in new_lgf:
    #        print(r)


    #print("first all_rows & mode filter:" + "*" * 50)
    lgfs = [lgf.split() for lgf in new_lgf]
    raw_lgf = new_lgf
    new_lgf = []

    has_select = False
    all_first_all = True
    for lgf in lgfs:
        if "(select_" in lgf[0]:
            has_select = True
            break
    for lgf in raw_lgf:
        if not "first all_rows" in lgf:
            all_first_all = False
            break

    for lgf in lgfs:
        layer = 0
        for l in lgf:
            if "(" in l:
                layer += 1
        if layer == 1:
            new_lgf.append(" ".join(lgf))
        elif (not (has_select and "(mode" in lgf[0])) and (all_first_all or "first all_rows" not in " ".join(lgf)):
            new_lgf.append(" ".join(lgf))

    #for r in raw_lgf:
    #    if r not in new_lgf:
    #        print(r)


    print("switch filter:" + "*" * 50)
    lgfs = [lgf.split() for lgf in new_lgf]
    raw_lgf = new_lgf
    new_lgf = []
    switch = set()
    for lgf in lgfs:
        for i in range(len(lgf) - 1):
            if "(" in lgf[i] and "(" in lgf[i + 1]:
                switch.add(lgf[i] + " " + lgf[i + 1])

    for lgf in lgfs:
        for i in range(len(lgf) - 1):
            if "(" in lgf[i] and "(" in lgf[i + 1] and lgf[i + 1] + " " + lgf[i] in switch:
                break
        else:
            new_lgf.append(" ".join(lgf))


    #for r in raw_lgf:
    #    if r not in new_lgf:
    #        print(r)


    #print("inside & outside nest filter:" + "*" * 50)
    raw_lgf = new_lgf
    new_lgf = []

    lgf_content_dic = collections.defaultdict(list)
    for lgf in raw_lgf:
        start = ""
        end = ""
        layers = 0
        for i in range(len(lgf)):
            if lgf[i] == "(":
                start = i
                layers += 1
            elif lgf[i] == ")":
                end = i
            if end:
                break
        if not end:
            continue
        key = lgf[start: end + 1]
        if key in lgf_content_dic:
            if layers == lgf_content_dic[key][0][1]:
                lgf_content_dic[key].append((lgf, layers))
            elif layers < lgf_content_dic[key][0][1]:
                lgf_content_dic[key] = []
                lgf_content_dic[key].append((lgf, layers))
        else:
            lgf_content_dic[key].append((lgf, layers))

    references = [k.split() for k in lgf_content_dic.keys()]
    for first_layer, values in lgf_content_dic.items():
        if not "(select" in first_layer[0]:
            for value in values:
                new_lgf.append(value[0])
        else:
            for value in values:
                tmp = value[0].replace(first_layer, "").replace("  ", " ")
                start = ""
                end = ""
                for i in range(len(tmp)):
                    if tmp[i] == "(":
                        start = i
                    elif tmp[i] == ")":
                        end = i
                    if end:
                        break
                if not end:
                    new_lgf.append(value[0])
                    continue
                second_layer = tmp[start: end + 1].split()
                for r in references:
                    if len(r) - len(second_layer) == 1:
                        diff_set = [i for i in r if not i in second_layer]
                        if len(diff_set) == 1:
                            #print(value[0])
                            #print("second_layer:")
                            #print(second_layer)
                            #print("reference:")
                            #print(r)
                            break
                else:
                    new_lgf.append(value[0])

    #for r in raw_lgf:
    #    if r not in new_lgf:
    #        print(r)


    lgf_len_dic = {}
    for lgf in new_lgf:
        lgf_len_dic[lgf] = len(lgf.split("("))
    sorted_res = sorted(lgf_len_dic.items(), key=lambda item:item[1])
    new_lgf = [s[0] for s in sorted_res]



    print("class filter:" + "*" * 50)
    raw_id = lgs_path[3:-3]
    if raw_id in ques_classes:
        cls = ques_classes[raw_id]
        print(ope_counts[cls])
        raw_lgf = new_lgf
        new_lgf = []
        for lgf in raw_lgf:
            opes = lgf.split()
            opes = [ope[1:] for ope in opes if "(" in ope]
            for ope in opes:
                if not ope in ope_counts[cls]:
                    break
            else:
                new_lgf.append(lgf)
        for r in raw_lgf:
            if r not in new_lgf:
                print(r)
    else:
        print(raw_id + "not in classes")

    print("final:" + "*" * 50)
    for logical_form in new_lgf:
        total = 0
        add = True
        if "diff all_rows" in logical_form or "same_as all_rows" in logical_form or "select_string all_rows" in logical_form or "select_number all_rows" in logical_form or "select_date all_rows" in logical_form:
            add = False
        for item in logical_form.split():
            #while item in logical_form:
            #    ori_item = item.split('(')[0] + "("
            #    logical_form = logical_form.replace(ori_item, "", 1).replace(")", "", 1)

            if "(" in item and item.strip("(") in filter_lst:
                total += 1
                if total > 1:
                    break
        if total <= 1 and add:
            final_lgf.append(logical_form)
    if final_lgf:
        coved += 1
        with gzip.open(new_dir + lgs_path, "wt") as fmodel:
            for l in final_lgf:
                print(l + "\n")
                fmodel.write(l + "\n")
    print("\n")
print(coved / 14152)
