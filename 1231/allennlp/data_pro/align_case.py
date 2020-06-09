import os
import gzip
from typing import Dict
import codecs

LOGICAL_FORM_NUM = 20


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


def align_operator(operator_dic, operators, question):
    """
    :param operator_dic: A dictionary maps operator to its corresponding trigger words
    :param operators: The operators of logical forms
    :param question:
    :return: bool, which indicates keep logical form for training or not
    """
    total = len(operators)
    if total == 0:
        return 0.0001
    aligned = 0
    for item in operators:
        #keep_flag = False
        trigger_lst = operator_dic[item]
        if trigger_lst:
            for trigger_word in trigger_lst:
                if trigger_word in question:
                    #keep_flag = True
                    aligned += 1
            #if not keep_flag:
            #    return False
        else:
            aligned += 1
    #return True
    return aligned / total


def parse_lgfs(logical_form, operator_dic):
    temp_lst = logical_form.split(' ')
    temp_operator, temp_column = [], []
    for item in temp_lst:
        if item.strip('(').strip(')') in operator_dic:
            temp_operator.append(item.strip('(').strip(')'))
        else:
            temp_column.append(item.strip('(').strip(')'))
    return temp_operator, temp_column


def align_column(lgfs_column, instance, table_dir):
    tpath = os.path.join(table_dir, instance['table_filename'].replace("csv", "tagged"))
    kg = table2kg(tpath)
    column_num = 0
    column_align_num = 0
    for item in lgfs_column:
        if "column" in item and item.split(':')[1] not in instance['question']:
            column_num += 1
            column_flag = False
            for word in instance['question'].split(' '):
                for cell in kg[item.split(':')[1]]:
                    if word in cell:
                        column_flag = True
                        break
                if column_flag:
                    break
            column_align_num += column_flag
        elif "column" in item and item.split(':')[1] in instance['question'].replace(" ", "_"):
            column_num += 1
            column_align_num += 1
        else:
            pass
    #if column_num == column_align_num:
    #    return True
    #else:
    #    return False
    if column_num == 0:
        return 0
    return column_align_num / column_num

def table2kg(tpath):
    kg = {}
    table_lines = [line.split("\t") for line in open(tpath).readlines()]
    print(table_lines)
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


operator_trigger = {"select_string": None,
                    "select_number": None,
                    "select_date": None,
                    "argmax": ["most", "largest", "highest", "longest", "greatest"],
                    "argmin": ["least", "smallest", "shortest", "lowest"],
                    "filter_number_greater": ["greater than", "more than", "larger than"],
                    "filter_number_greater_equals": ["at least"],
                    "filter_number_lesser": ["less than", "smaller than"],
                    "filter_number_lesser_equals": ["no more than", "no greater than", "no larger than", "at most"],
                    "filter_number_equals": None,
                    "filter_number_not_equals": None,
                    "filter_date_greater": ["after"],
                    "filter_date_greater_equals": None,
                    "filter_date_lesser": ["before"],
                    "filter_date_lesser_equals": None,
                    "filter_date_equals": None,
                    "filter_date_not_equals": ["not"],
                    "filter_in": None,
                    "filter_not_in": ["not", "other", "besides"],
                    "first": ["first", "top"],
                    "last": ["last", "bottom"],
                    "previous": ["previous", "above", "before"],
                    "next": ["next", "below", "after"],
                    "count": ["how many"],
                    "max_number": ["most"],
                    "min_number": ["least"],
                    "max_date": ["last"],
                    "min_date": ["first"],
                    "sum": ['total'],
                    "average": ["average"],
                    "mode_string": None,
                    "mode_number": None,
                    "mode_date": None,
                    "same_as": ["same"],
                    "diff": ["difference", "how many more", "how much more"],
                    "all_rows": None
                    }

lgs_dir = "/home/xuzh/mnt/allennlp/nsm_allen/searched_lfs_with_rules_no_conservative/"
new_dir = "/home/xuzh/mnt/allennlp/nsm_allen/lgfs_align_operator_column_new/"
input_examples_file = "/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/data/training.examples"
table_path = "/home/xuzh/mnt/allennlp/nsm_allen/WikiTableQuestions/"
case_file = "case_tmp.txt"
data_examples = {parse_example_line(example_line)['id']: parse_example_line(example_line) for example_line in
                 open(input_examples_file)}
cf = codecs.open(case_file, mode="a")

for lgs_path in os.listdir(lgs_dir):
    g_file = gzip.open(lgs_dir + lgs_path)
    line_idx = 0
    new_lgs_lst = []
    for logical_form in g_file:
        line_idx += 1
        logical_form = logical_form.strip().decode('utf-8')
        #print("lgf:")
        #print(logical_form)
        operator, column = parse_lgfs(logical_form, operator_trigger)
        #operator_flag = align_operator(operator_trigger, operator, data_examples[lgs_path.split('.')[0]]['question'])
        #column_flag = align_column(column, data_examples[lgs_path.split('.')[0]], table_path)

        #if line_idx <= LOGICAL_FORM_NUM and column_flag and operator_flag:
        #print("operator")
        #print(operator)
        #print("column")
        #print(column)
        data = data_examples[lgs_path.split('.')[0]]
        operator_score = align_operator(operator_trigger, operator, data['question'])
        #print("ope_score" + str(operator_score))
        column_score = align_column(column, data, table_path)
        #print("column_score" + str(column_score))
        if operator_score == 1 and column_score == 1:
            new_lgs_lst.append(data['question'] + "|" + logical_form + "|" + str(operator_score + column_score) + "\n")
    cf.write("".join(new_lgs_lst))
    #if new_lgs_lst:
    #    with gzip.open(new_dir+lgs_path, "wt") as fmodel:
    #        for lgf in new_lgs_lst:
    #            fmodel.write(lgf)
