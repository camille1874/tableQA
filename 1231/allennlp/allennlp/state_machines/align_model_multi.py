#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import time
import datetime
from allennlp.state_machines.preprocess_multi import Word2Vec, MData
from allennlp.state_machines import data_helpers
from allennlp.state_machines.text_cnn_multi import TextCNN
from tensorflow.contrib import learn
import csv
import sys 
import math

class Classification(object):
    def __init__(self, batch_size=1, checkpoint_dir="/home/xuzh/new1/multi_class/runs/1576122712/checkpoints/"): 
        self.checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)
        self.word2vec = Word2Vec()
        self.test_data = MData(word2vec=self.word2vec)
        self.batch_size = batch_size
        self.graph = tf.Graph()
        with self.graph.as_default():
            session_conf = tf.ConfigProto(
                allow_soft_placement=True,
                log_device_placement=False)
            session_conf.gpu_options.allow_growth=True
            self.sess = tf.Session(config=session_conf)
            with self.sess.as_default():
                saver = tf.train.import_meta_graph("{}.meta".format(self.checkpoint_file))
                saver.restore(self.sess, self.checkpoint_file)





    
    def get_score(self, question, table, lgf, predict_score, raw_align_score):
        self.test_data.get_data(question, str(table), lgf, predict_score, raw_align_score)
        x_test_batch, _, features_batch = self.test_data.next_batch(batch_size=self.batch_size)
        input_x = self.graph.get_operation_by_name("input_x").outputs[0]
        features = self.graph.get_operation_by_name("features").outputs[0]
        dropout_keep_prob = self.graph.get_operation_by_name("dropout_keep_prob").outputs[0]
        #predictions = self.graph.get_operation_by_name("output/predictions").outputs[0]
        #batch_scores = self.sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
        scores = self.graph.get_operation_by_name("output/scores").outputs[0]
        batch_scores = self.sess.run(scores, {input_x: x_test_batch, dropout_keep_prob: 1.0, features: features_batch})
        return batch_scores[0][1] - batch_score[0][0]


    def get_score_multi(self, question, table, lgf, predict_score):
        self.test_data.get_data(question, str(table), lgf, predict_score)
        x_test_batch, _, features_batch = self.test_data.next_batch(batch_size=self.batch_size)
        input_x = self.graph.get_operation_by_name("input_x").outputs[0]
        features = self.graph.get_operation_by_name("features").outputs[0]
        dropout_keep_prob = self.graph.get_operation_by_name("dropout_keep_prob").outputs[0]
        scores = self.graph.get_operation_by_name("output/scores").outputs[0]
        batch_scores = self.sess.run(scores, {input_x: x_test_batch, dropout_keep_prob: 1.0, features: features_batch})
        batch_scores = data_helpers.softmax(batch_scores)
        #return  batch_scores[0][2] * 2 + batch_scores[0][1] - batch_scores[0][0]
        return batch_scores[0][2]

