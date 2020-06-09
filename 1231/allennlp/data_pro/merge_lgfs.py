import os
import gzip
import random

full_path = '/home/xuzh/mnt/allennlp/nsm_allen/searched_lfs_with_rules_no_conservative/'
full_lgfs = {fpath: None for fpath in os.listdir(full_path)}

part_path = '/home/xuzh/mnt/allennlp/nsm_allen/lgfs_align_operator_column/'
part_lgfs = {fpath: None for fpath in os.listdir(part_path)}

output_dir = '/home/xuzh/mnt/allennlp/nsm_allen/lgfs_tmp/'
os.mkdir(output_dir)
merged_list = []

for item in full_lgfs:
    if item not in part_lgfs:
        merged_list.append(full_path + item)
    else:
        merged_list.append(part_path + item)

for l_item in merged_list:
    output = gzip.open(output_dir + l_item.rsplit('/', 1)[1], "wt")
    with gzip.open(l_item) as fmodel:
        for logical_form in fmodel:
            output.write(logical_form.strip().decode('utf-8') + "\n")

