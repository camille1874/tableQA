#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import time
import datetime
from preprocess import Word2Vec, MData
import data_helpers
from text_cnn_multi import TextCNN
from tensorflow.contrib import learn
import csv
import sys 

# Parameters
# ==================================================

# Data Parameters
tf.flags.DEFINE_string("final_x", "test_x_multi.txt", "Data source for the positive data.")
tf.flags.DEFINE_string("final_y", "test_y_multi.txt", "Data source for the negative data.")

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_dir", "", "Checkpoint directory from training run")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")


FLAGS = tf.flags.FLAGS
#FLAGS._parse_flags()
FLAGS(sys.argv)

print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")



x_raw = list(open(FLAGS.final_x, "r").readlines())
x_raw = [s.strip() for s in x_raw]
y_test = list(open(FLAGS.final_y, "r").readlines())
y_test = [s.strip() for s in y_test]
y_test = list(map(int, y_test))
x_raw = [data_helpers.clean_str(sent) for sent in x_raw]
w = Word2Vec()
test_data = MData(word2vec=w)
test_data.open_file_final(FLAGS.final_x, FLAGS.final_y)



print("\nEvaluating...\n")

checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    session_conf.gpu_options.allow_growth=True
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        input_x = graph.get_operation_by_name("input_x").outputs[0]
        features = graph.get_operation_by_name("features").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        predictions = graph.get_operation_by_name("output/predictions").outputs[0]


        all_predictions = np.zeros(len(test_data.s))

        i = 0
        while test_data.is_available():
            x_test_batch, _, features_batch = test_data.next_batch(batch_size=FLAGS.batch_size)
            batch_scores = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0, features: features_batch})
            all_predictions[i: i + len(x_test_batch)] = batch_scores
            i += len(x_test_batch)


# Print accuracy if y_test is defined
if y_test is not None:
    correct_predictions = float(sum(all_predictions == y_test))
    print("Total number of test examples: {}".format(len(y_test)))
    print("Accuracy: {:g}".format(correct_predictions/float(len(y_test))))

# Save the evaluation to a csv
predictions_human_readable = np.column_stack((np.array(x_raw), all_predictions))
out_path = os.path.join(FLAGS.checkpoint_dir, "..", "prediction.csv")
print("Saving evaluation to {0}".format(out_path))
with open(out_path, 'w') as f:
    csv.writer(f).writerows(predictions_human_readable)
