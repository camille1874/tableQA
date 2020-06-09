# -*- encoding:utf-8 -*-
import numpy as np
import gensim
import codecs
import numpy.random as random
from data_helpers import clean_str
from bert_serving.client import BertClient
import logging

logger = logging.getLogger(__name__)


class Bert():
    def __init__(self):
        self.model = BertClient(check_length=False)
    
    def get(self, sens):
        return self.model.encode([sens])
    # ['aaa', 'bbb']
    # ['a a a ||| b b b'] for pair


class Data():
    def __init__(self, emb, max_len=20, shuffle=True):
        self.s, self.labels, self.features = [], [], []
        self.index, self.max_len, self.emb = 0, max_len, emb
        self.shuffle = shuffle
  
    def open_file(self):
        pass

    def is_available(self):
        if self.index < self.data_size:
            return True
        else:
            return False

    def reset_index(self):
        self.index = 0
        if self.shuffle == True:
            random.seed(20)
            random.shuffle(self.s) 
            random.seed(20)
            random.shuffle(self.features)
            random.seed(20)
            random.shuffle(self.labels)

    def next(self):
        if (self.is_available()):
            self.index += 1
            return self.data[self.index - 1]
        else:
            return

    def next_batch(self, batch_size):
        batch_size = min(self.data_size - self.index, batch_size)
        s_mats = []

        for i in range(batch_size):
            s = self.s[self.index + i]

            #s_mats.append(np.expand_dims(np.pad(np.column_stack([self.emb.get(w) for w in s]),
            #                                     [[0, 0], [0, self.max_len - len(s)]],
            #                                     "constant"), axis=0))
            s_mats.append(self.emb.get(s))

        batch_s = np.concatenate(s_mats, axis=0)
        #batch_s = batch_s.transpose((0, 2, 1))
        batch_labels = self.labels[self.index:self.index + batch_size]
        batch_features = self.features[self.index:self.index + batch_size]
        
        self.index += batch_size

        return batch_s, batch_labels, batch_features



class MData(Data):
    def open_file(self, pos_file, neg_file):
        pos = codecs.open(pos_file, encoding="utf-8").readlines()
        neg = codecs.open(neg_file, encoding="utf-8").readlines()
        data = pos + neg
        self.features = [[float(x.split("\t")[-2]), float(x.strip().split("\t")[-1])] for x in data]
        #data = ["\t".join(x.split("\t")[:-2]) for x in data]
        data = [clean_str(x.split("\t")[0]) + " ||| " + clean_str(x.split("\t")[2]) for x in data]
        #data = [clean_str(x).split(" ") for x in data]
        #self.s = np.array(data)
        self.s = data
        pos_labels = [[0, 1]] * len(pos)
        neg_labels = [[1, 0]] * len(neg)
        self.labels = np.concatenate([pos_labels, neg_labels], 0)
        random.seed(10)
        random.shuffle(self.s) 
        random.seed(10)
        random.shuffle(self.features)
        random.seed(10)
        random.shuffle(self.labels)

        #local_max_len = max([len(x) for x in self.s])
        #if local_max_len > self.max_len:
        #    self.max_len = local_max_len

        self.data_size = len(self.s)
        self.num_features = len(self.features[0])    


    def open_file_final(self, x_file, y_file):
        xs = codecs.open(x_file, encoding="utf-8").readlines()
        ys = codecs.open(y_file, encoding="utf-8").readlines()
        self.features = [[float(x.split("\t")[-2]), float(x.strip().split("\t")[-1])] for x in xs]
        #xs = [clean_str("\t".join(x.split("\t")[:-2])).split(" ")[:self.max_len] for x in xs]
        xs = [clean_str(x.split("\t")[0]) + " ||| " + clean_str(x.split("\t")[2]) for x in xs]
        for i in range(5):
            logger.info(xs[i])
        ys = [int(x.strip()) for x in ys]
        #self.s = np.array(xs)
        self.s = xs
        new_y = []
        for y in ys:
            if y == 1:
                new_y.append([0, 1])
            elif y == 0:
                new_y.append([1, 0])
        self.labels = np.array(new_y)

        local_max_len = max([len(x) for x in self.s])
        if local_max_len > self.max_len:
            self.max_len = local_max_len

        self.data_size = len(self.s)
        self.num_features = len(self.features[0])    
   

    def get_data(self, question, table, lgf, predict_score, raw_align_score):
        #xs = question + "\t" + table + "\t" + lgf
        #xs = [clean_str(xs).split(" ")[:self.max_len]]
        xs = [clean_str(question) + " ||| " + clean_str(lgf)]
        logger.info(xs[0])
        self.s = np.array(xs)
        self.features = [[raw_align_score, predict_score]]

        local_max_len = max([len(x) for x in self.s])
        if local_max_len > self.max_len:
            self.max_len = local_max_len

        self.index = 0
        self.data_size = 5000
        self.num_features = len(self.features[0])    
