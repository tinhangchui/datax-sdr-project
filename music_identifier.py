"""
TODO: Come up with a machine learning model to identify if
a .wav file is music.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

import tensorflow as tf
from tensorflow.contrib.framework.python.ops import audio_ops as contrib_audio
FLAGS = None

def load_graph(filename):
  """Unpersists graph from file as default graph."""
  with tf.gfile.FastGFile(filename, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    tf.import_graph_def(graph_def, name='')


def load_labels(filename):
  """Read in labels, one label per line."""
  return [line.rstrip() for line in tf.gfile.GFile(filename)]

def run_graph(wav_data, labels, input_layer_name, output_layer_name,
              num_top_predictions):
  """Runs the audio data through the graph and prints predictions."""
  with tf.Session() as sess:
    # Feed the audio data as input to the graph.
    #   predictions  will contain a two-dimensional array, where one
    #   dimension represents the input image count, and the other has
    #   predictions per class
    softmax_tensor = sess.graph.get_tensor_by_name(output_layer_name)
    predictions, = sess.run(softmax_tensor, {input_layer_name: wav_data})

    # Sort to show labels in order of confidence
    top_k = predictions.argsort()[-num_top_predictions:][::-1]
    for node_id in top_k:
      human_string = labels[node_id]
      score = predictions[node_id]
      print('%s (score = %.5f)' % (human_string, score))

    return labels[top_k[0]] == 'music'

labels_list = load_labels('./speech_commands_train/conv_labels.txt')
load_graph('./my_frozen_graph.pb')

def is_music(filename):
    """
    Given the filename(a .wav file), open the file and see if it is music.
    Return true if it is music. False otherwise.
    """
    with open(filename, 'rb') as wav_file:
        wav_data = wav_file.read()
        return run_graph(wav_data, labels_list, 'wav_data:0', 'labels_softmax:0', 3)
    return False
