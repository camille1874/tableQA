import os
import gzip
import codecs
from typing import Dict

#LOGICAL_FORM_NUM = 20
LOGICAL_FORM_NUM = 10


def parse_example_line(lisp_string: str) -> Dict:
    """
    Training data in WikitableQuestions comes with examples in the form of lisp strings in the format:
        (example (id <example-id>)
                 (utterance <question>)
                 (context (graph tables.TableKnowledgeGraph <table-filename>))
                 (targetValue (list (description <answer1>) (description <answer2>) ...)))

    We parse such strings and return the parsed information here.
    """
    id_piece, rest = lisp_string.split(') (utterance "')
    example_id = id_piece.split('(id ')[1]
    question, rest = rest.split('") (context (graph tables.TableKnowledgeGraph ')
    table_filename, rest = rest.split(')) (targetValue (list')
    target_value_strings = rest.strip().split("(description")
    target_values = []
    for string in target_value_strings:
        string = string.replace(")", "").replace('"', '').strip()
        if string != "":
            target_values.append(string)
    return {'id': example_id,
            'question': question,
            'table_filename': table_filename,
            'target_values': target_values}




def table2kg(tpath):
    kg = {}
    table_lines = [line.split("\t") for line in open(tpath).readlines()]
    index = 1
    idx2row = {}
    while table_lines[index][0] == "-1":
        column_name = table_lines[index][2].replace('fb:row.row.', '')
        kg[column_name] = []
        idx2row[table_lines[index][1].strip()] = column_name
        index += 1
    for line in table_lines[index:]:
        if line[1] in idx2row:
            kg[idx2row[line[1]]].append(line[2].replace('fb:cell.', ''))
    return kg

def get_res(log_path):
    select_lines = codecs.open(log_path).readlines()
    i = 0
    res = {}
    while '*decoding:*' not in select_lines[i]:
        i += 1
    while i < len(select_lines):
        question = select_lines[i + 5].split(" - ")[-1].strip()
        table = select_lines[i + 7].split(" - ")[-1].strip()
        i += 1
        rec = {}
        while 'selected_logical_form:' not in select_lines[i]:
            #rec[select_lines[i + 8].split(" - ")[-1].strip()] = (float(select_lines[i + 2].split(" - ")[-1].strip()), float(select_lines[i + 10].split(" - ")[-1].strip()))
            #i += 11
            rec[select_lines[i + 8].split(" - ")[-1].strip()] = (float(select_lines[i + 2].split(" - ")[-1].strip()), float(select_lines[i + 11].split(" - ")[-1].strip()))
            i += 12
        res[question + table] = rec
        while i < len(select_lines) and '*decoding:*' not in select_lines[i]:
            i += 1
    return res


def align():
    lgs_dir = "/home/xuzh/mnt/allennlp/nsm_allen/searched_lfs_with_rules_no_conservative/"
    #new_dir = "/home/xuzh/mnt/allennlp/nsm_allen/lgfs_align_model_t/"
    new_dir = "/home/xuzh/mnt/allennlp/nsm_allen/lgfs_align_operator_column_new_1213/"
    input_examples_file = "/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/data/training.examples"
    #input_examples_file = "/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/data/random-split-1-train.examples"
    table_path = "/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/"
    log_path = "/home/xuzh/new1/allennlp/weak_supervision/log_1213_train.txt"
    #log_path = "/home/xuzh/new1/allennlp/weak_supervision/log_1208_model_align_train_all_1213.txt"
    res = get_res(log_path)

    data_examples = {parse_example_line(example_line)['id']: parse_example_line(example_line) for example_line in
                     open(input_examples_file)}
    
    for lgs_path in os.listdir(lgs_dir):
        g_file = gzip.open(lgs_dir + lgs_path)
        new_lgs_lst = {}
        for logical_form in g_file:
            logical_form = logical_form.strip().decode('utf-8')
            instance = data_examples[lgs_path.split('.')[0]]
            question = instance['question']
            tpath = os.path.join(table_path, instance['table_filename'].replace("csv", "tagged"))
            table = str(table2kg(tpath))
            if question + table in res and logical_form in res[question + table]:
                cands = res[question + table]
                score = cands[logical_form]
                
                score = score[1]
                if score < 10e-4:
                    score = 0.0001
                
                #if score[1] < 0:
                #    score = 0.0001
                #else:
                #    score = score[1] / 5
                
                new_lgs_lst[logical_form + "|" + str(score) + "\n"] = score
            #new_lgf = res[question + table]
            #for k, v in new_lgf.items():
            #    new_lgs_lst[k + "|" + str(v[1]) + "\n"] = v[1]
        new_lgs_lst = sorted(new_lgs_lst.items(), key=lambda item:item[1], reverse=True)[:LOGICAL_FORM_NUM]
        new_lgs_lst = [x[0] for x in new_lgs_lst]
        if new_lgs_lst:
            with gzip.open(new_dir+lgs_path, "wt") as fmodel:
                for lgf in new_lgs_lst[:LOGICAL_FORM_NUM]:
                    fmodel.write(lgf)


align()
