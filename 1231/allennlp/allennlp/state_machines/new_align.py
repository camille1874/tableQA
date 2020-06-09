import os
import gzip
from typing import Dict
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import logging

LOGICAL_FORM_NUM = 20
logger = logging.getLogger(__name__)

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


def align_column(lgfs_column, question, kg):
    column_num = 0
    column_align_num = 0
    for item in lgfs_column:
        if "column" in item:
            column_num += 1
            #if (item.split(':')[1] in question) or (item.split(':')[1] in question.replace(" ", "_")):
            if item.split(':')[1] in question:
                logger.info("&" * 50)
                logger.info(question)
                logger.info(lgfs_column)
            column_flag = False
            for word in question:
                if word in item.split(':')[1]:
                    column_flag = True
                else:
                    for cell in kg[item.split(':')[1]]:
                        if word in cell:
                            column_flag = True
                            break
                if column_flag:
                    break
            column_align_num += column_flag
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


def get_sim(word1, word2):
    try:
        sim = model.similarity(word1, word2)
        return sim
    except:
        return None


def align(logical_form, question, table):
    #model = 
    #stop = stopwords.words("english") 
    #停用词需要简化
    stop = ["of", "by", "at", "in", "on", "with", "from", "about", "under", "to", "a"]
    filtered_question = [word for word in question.split(' ') if word not in stop and len(word) > 1]
    operator, column = parse_lgfs(logical_form, operator_trigger)
    operator_score = align_operator(operator_trigger, operator, question) 
    #trigger word可能是词组，不能先对question进行处理
    column_score = align_column(column, filtered_question, table)
    score = (operator_score + column_score) / 2
    return score
