import gzip
import os

filter_lst = ['first (first', "first (last", "last (first", "last (last"]
g_file = gzip.open("/home/geshi/test/dir1/nt-202.gz")
lgs_dir = "/home/geshi/nsm_allen/searched_lfs_with_rules_no_conservative/"
new_dir = "/home/geshi/nsm_allen/lgfs_wo_redundancy/"

for lgs_path in os.listdir(lgs_dir):
    g_file = gzip.open(lgs_dir + lgs_path)
    # new_gfile = open(new_dir+lgs_path, "wt")
    with gzip.open(new_dir+lgs_path, "wt") as fmodel:
        for logical_form in g_file:
            logical_form = logical_form.strip().decode('utf-8')
            for item in filter_lst:
                while item in logical_form:
                    ori_item = item.split('(')[0] + "("
                    logical_form = logical_form.replace(ori_item, "", 1).replace(")", "", 1)
            # new_gfile.write(logical_form+"\n")
            # print(logical_form)
            fmodel.write(logical_form+"\n")
    # new_gfile.close()
            # print(logical_form.strip().decode('utf-8'))

# with gzip.open("test.gz", "wt") as fmodel:
#     for logical_form in g_file:
#         print(logical_form.strip().decode('utf-8'))
#         fmodel.write(logical_form.strip().decode('utf-8'))