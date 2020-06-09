import os

train_file = "/home/geshi/nsm_allen/WikiTableQuestions/data/random-split-1-train.examples"
lgfs_path = "/home/geshi/nsm_allen/searched_lfs_with_rules_no_conservative/"

lgfs_lst = {fname.split('.')[0]:None for fname in os.listdir(lgfs_path)}
# print(lgfs_lst)
out_lgs = open("/home/geshi/nsm_allen/WikiTableQuestions/data/random-split-1-train-with-lgfs.examples", "w")
out_no_lgs = open("/home/geshi/nsm_allen/WikiTableQuestions/data/random-split-1-train-wo-lgfs.examples", "w")
with open(train_file) as fmodel:
    for line in fmodel:
        id = line.strip().split('(')[2].strip(') ').split(' ')[1]
        if id in lgfs_lst:
            out_lgs.write(line)
        else:
            out_no_lgs.write(line)

out_lgs.close()
out_no_lgs.close()