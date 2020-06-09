import os
import gzip
from typing import Dict
import gensim
import numpy as np

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


def align_operator(w2v_model, operator_dic, operators, question):
    """
    :param operator_dic: A dictionary maps operator to its corresponding trigger words
    :param operators: The operators of logical forms
    :param question:
    :return: bool, which indicates keep logical form for training or not
    """
    question = question.replace("?", "")
    score = 0.0001
    if not operators:
        return score
    ques_words = question.split()
    for item in operators:
        trigger_lst = operator_dic[item]
        if not trigger_lst:
            continue
        for trigger_words in trigger_lst:
            for qw in ques_words:
                for tw in trigger_words.split():
                    tmp_score = w2v_model.get_sim(tw, qw)
                    if tmp_score > score:
                        score = tmp_score		
    return score


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
    score = 0.0001
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
        return score
    return score + column_align_num / column_num

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




def align(w2v_model):
    lgs_dir = "/home/xuzh/1231/data/searched_lfs_with_rules_no_conservative/"
    #new_dir = "/home/xuzh/1231/data/lgfs_align_operator_column_w2v_1/"
    new_dir = "/home/xuzh/1231/data/lgfs_align_operator_column_w2v_2/"
    input_examples_file = "/home/xuzh/1231/data/WikiTableQuestions/data/training.examples"
    table_path = "/home/xuzh/1231/data/WikiTableQuestions/"
    
    data_examples = {parse_example_line(example_line)['id']: parse_example_line(example_line) for example_line in
                     open(input_examples_file)}
    
    for lgs_path in os.listdir(lgs_dir):
        g_file = gzip.open(lgs_dir + lgs_path)
        new_lgs_lst = {}
        for logical_form in g_file:
            logical_form = logical_form.strip().decode('utf-8')
            operator, column = parse_lgfs(logical_form, operator_trigger)
            operator_score = align_operator(w2v_model, operator_trigger, operator, data_examples[lgs_path.split('.')[0]]['question'])
            #column_score = align_column(column, data_examples[lgs_path.split('.')[0]], table_path)
            #score = operator_score + column_score
            score = operator_score
            new_lgs_lst[logical_form + "|" + str(score) + "\n"] = score
        new_lgs_lst = sorted(new_lgs_lst.items(), key=lambda item:item[1], reverse=True)[:LOGICAL_FORM_NUM]
        new_lgs_lst = [x[0] for x in new_lgs_lst]
        if new_lgs_lst:
            with gzip.open(new_dir + lgs_path, "wt") as fmodel:
                for lgf in new_lgs_lst[:LOGICAL_FORM_NUM]:
                    fmodel.write(lgf)


class Word2Vec():
    def __init__(self):
        self.model = gensim.models.KeyedVectors.load_word2vec_format('/home/xuzh/GoogleNews-vectors-negative300.bin', binary=True)
        self.unknowns = np.random.uniform(-0.01, 0.01, 300).astype("float32")

    def get(self, word):
        if word not in self.model.vocab:
            return self.unknowns
        else:
            return self.model.word_vec(word)


    def get_sim(self, word1, word2):
        print(word1, word2)
        try:
            sim = self.model.similarity(word1, word2)
        except:
            sim = 0
	print(sim)
        #vec1 = self.get(word1)
        #vec2 = self.get(word2)
        #dis = np.sqrt(np.sum(np.square(vec1 - vec2)))
        #sim = 1 / (1 + np.exp(-dis))
        #print(sim)
        return sim



w2v_model = Word2Vec()
align(w2v_model)
#m = Word2Vec()
#m.get_sim("father", "mother")
#m.get_sim("father", "son")
#m.get_sim("beautiful", "pretty")
#m.get_sim("beautiful", "ugly")
