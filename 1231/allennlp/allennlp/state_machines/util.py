from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Union

import torch
import numpy as np
import gensim
import logging
from scipy.linalg import norm

logger = logging.getLogger(__name__)

def construct_prefix_tree(targets: Union[torch.Tensor, List[List[List[int]]]],
                          target_mask: Optional[torch.Tensor] = None,
                          #weights: List[float] = None) -> List[Dict[Tuple[int, ...], Set[int]]]:
                          weights: List[List[float]] = None) -> List[Dict[Tuple[int, ...], Dict[int, float]]]:
    """
    Takes a list of valid target action sequences and creates a mapping from all possible
    (valid) action prefixes to allowed actions given that prefix.  While the method is called
    ``construct_prefix_tree``, we're actually returning a map that has as keys the paths to
    `all internal nodes of the trie`, and as values all of the outgoing edges from that node.

    ``targets`` is assumed to be a tensor of shape ``(batch_size, num_valid_sequences,
    sequence_length)``.  If the mask is not ``None``, it is assumed to have the same shape, and
    we will ignore any value in ``targets`` that has a value of ``0`` in the corresponding
    position in the mask.  We assume that the mask has the format 1*0* for each item in
    ``targets`` - that is, once we see our first zero, we stop processing that target.

    For example, if ``targets`` is the following tensor: ``[[1, 2, 3], [1, 4, 5]]``, the return
    value will be: ``{(): set([1]), (1,): set([2, 4]), (1, 2): set([3]), (1, 4): set([5])}``.

    This could be used, e.g., to do an efficient constrained beam search, or to efficiently
    evaluate the probability of all of the target sequences.
    """
    #batched_allowed_transitions: List[Dict[Tuple[int, ...], Set[int]]] = []
    batched_allowed_transitions: List[Dict[Tuple[int, ...], Dict[int, float]]] = []

    if not isinstance(targets, list):
        assert targets.dim() == 3, "targets tensor needs to be batched!"
        targets = targets.detach().cpu().numpy().tolist()
    if target_mask is not None:
        target_mask = target_mask.detach().cpu().numpy().tolist()
    else:
        target_mask = [None for _ in targets]

    #for instance_targets, instance_mask in zip(targets, target_mask):
    for instance_targets, ws in zip(targets, weights):
        #allowed_transitions: Dict[Tuple[int, ...], Set[int]] = defaultdict(set)
        allowed_transitions: Dict[Tuple[int, ...], Dict[int, float]] = defaultdict(dict)
        for i, target_sequence in enumerate(instance_targets):
            history: Tuple[int, ...] = ()
            for j, action in enumerate(target_sequence):
                #if instance_mask and instance_mask[i][j] == 0:
                #    break
               # if action in allowed_transitions[history]:
               #     allowed_transitions[history][action] += float(ws[i])
               #     #allowed_transitions[history][action] = max(allowed_transitions[history][action], float(ws[i]))
               # else:
               #     allowed_transitions[history][action] = float(ws[i])
               
                #if j == len(target_sequence) - 1:
                #    allowed_transitions[history][action] = float(ws[i]) 
                #else:
                allowed_transitions[history][action] = 0
                history = history + (action,)
        #for h, v in allowed_transitions.items():
        #    for a in v:
        #        if h + (a,) in allowed_transitions:
        #            v[a] /= len(allowed_transitions[h + (a,)])

        batched_allowed_transitions.append(allowed_transitions)
    return batched_allowed_transitions


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
                    "mode_string": ["most"],
                    "mode_number": ["most"],
                    "mode_date": ["most"],
                    "same_as": ["same"],
                    "diff": ["difference", "how many more", "how much more"],
                    "all_rows": None
                    }


class Word2Vec():
    def __init__(self):
        self.model = gensim.models.KeyedVectors.load_word2vec_format('/home/xuzh/GoogleNews-vectors-negative300.bin', binary=True)
        self.unknowns = np.random.uniform(-0.01, 0.01, 300).astype("float32")

    def get(self, word):
        if word not in self.model.vocab:
            return self.unknowns
        else:
            return self.model.word_vec(word)

    def get_sentence_sim(sen1, sen2):
        def sentence_vector(s):
            words = s.split()
            v = np.zeros(300)
            for word in words:
                if word in self.model:
                    v += self.model[word]
            v /= len(words)
            return v
        v1, v2 = sentence_vector(sen1), sentence_vector(sen2)
        return np.dot(v1, v2) / (norm(v1) * norm(v2))

    


    def get_sim(self, word1, word2):
        #print(word1, word2)
        try:
            sim = self.model.similarity(word1, word2)
        except:
            sim = 0
        #print(sim)
        #vec1 = self.get(word1)
        #vec2 = self.get(word2)
        #dis = np.sqrt(np.sum(np.square(vec1 - vec2)))
        #sim = 1 / (1 + np.exp(-dis))
        #print(sim)
        return sim


def parse_action(action, operator_dic):
    temp_action = action.split(' ')
    temp_operator = {}
    for item in temp_action:
        if item in operator_dic:
            temp_operator[item] = operator_dic[item]
    return temp_operator


def get_weights(group_index, action_ids, action_mapping, question, w2v_model):
    logger.info("#" * 50)
    logger.info(question)
    ques_words = question.replace("?", "").split()
    scores = [0.001] * len(action_ids)
    try:
        action_strings = [action_mapping[(group_index, action_index)] for action_index in action_ids]
    except Exception as e:
        logger.info(e)
        return torch.tensor(scores).cuda()
       
    for idx, action in enumerate(action_strings):
        logger.info("*" * 50)
        logger.info(idx)
        logger.info(action)
        operators = parse_action(action, operator_trigger)
        if not operators:
            logger.info("No operators or no trigger words.")
            continue
        score = 0.2 #没有trigger word或trigger word为词组（比较固定）但问句中没有出现
        find = False
        #不过应该只有一个operator
        for operator, trigger_lst in operators.items():
            logger.info(operator)
            if not trigger_lst:
                continue
            for trigger_words in trigger_lst:
                if trigger_words in question:
                    score = 1
                    find = True
                    break
                elif len(trigger_words.split()) == 1:
                    tw = trigger_words
                    for qw in ques_words:
                        tmp_score = w2v_model.get_sim(tw, qw)
                        if tmp_score > score:
                            score = tmp_score
            if find:
                break
            logger.info(score)
        scores[idx] = score
    return torch.tensor(scores).cuda()