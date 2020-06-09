import re
import os
import shutil
import gzip

lg_path = '/home/geshi/nsm_allen/searched_lfs_with_rules_no_conservative/'
lg_path1 = '/home/geshi/nsm_allen/lgfs_align_operator_column/'
lg_path2 = ''

gz_lst = os.listdir(lg_path)
total = 0.0

gz_lst1 = os.listdir(lg_path1)
total1 = 0.0


for gz_file in gz_lst:
    temp_file = gzip.open(lg_path+gz_file)
    for logical_form in temp_file:
        total += 1
print(total/len(gz_lst))


for gz_file1 in gz_lst1:
    temp_file1 = gzip.open(lg_path1+gz_file1)
    for logical_form in temp_file1:
        total1 += 1
print(total1/len(gz_lst1))
