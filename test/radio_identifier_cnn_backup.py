"""
TODO: scan the radio. Use machine learning to identify FM stations.
The UI will use get_radio_list() to get the list of FM stations frequencies.
"""
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from numpy import *
from numpy.fft import *
from matplotlib.pyplot import *
from rtlsdr import RtlSdr

def cnn_model_fn(features, labels, mode):
  """Model function for CNN."""
  # Input Layer
  input_layer = tf.reshape(features["x"], [-1, 1, 2048, 1])

  # Convolutional Layer #1
  conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=32,
      kernel_size=[1, 5],
      padding="same",
      activation=tf.nn.relu)

  # Pooling Layer #1
  pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[1, 4], strides=4)

  # Convolutional Layer #2 and Pooling Layer #2
  conv2 = tf.layers.conv2d(
      inputs=pool1,
      filters=64,
      kernel_size=[1, 5],
      padding="same",
      activation=tf.nn.relu)
  pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[1, 4], strides=4)

  # Dense Layer
  pool2_flat = tf.reshape(pool2, [-1, 2048//4//4 * 64])

  dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)
  dropout = tf.layers.dropout(
      inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

  # Logits Layer
  logits = tf.layers.dense(inputs=dropout, units=2)

  predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      "classes": tf.argmax(input=logits, axis=1),
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
  }

  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

  # Calculate Loss (for both TRAIN and EVAL modes)
  loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

  # Configure the Training Op (for TRAIN mode)
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    train_op = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

  # Add evaluation metrics (for EVAL mode)
  eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])}
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

def read_frequency(fq):
    sdr = RtlSdr()

    # Set parameters
    sampling_rate = 2400000
    center_freq = fq * 1.000e6
    # print(sdr.valid_gains_db)
    gain = 40.2

    sdr.set_sample_rate(sampling_rate)
    sdr.set_center_freq(center_freq)
    sdr.set_gain(gain)

    time_duration = 1 # if noisy plot try longer duration
    N_Samples = sampling_rate * time_duration
    y = sdr.read_samples(N_Samples) # comment out after collecting data
    # y = np.load(str(int(center_freq)) + ".npy")	# uncomment after collecting data
    sdr.close()

    interval = 2048
    chunks = N_Samples//interval
    N = interval * chunks

    y = y[:N]
    # np.save(str(int(center_freq)), y)	# comment out after collecting data

    # Calculate average power spectrum
    y = y[:len(y//interval*interval)]
    y = y.reshape(N//interval, interval)
    y_windowed = y*np.kaiser(interval, 6)
    Y = fftshift(fft(y_windowed,axis=1),axes=1)

    Pspect = mean(abs(Y)*abs(Y),axis=0);
    return Pspect

mnist_classifier = tf.estimator.Estimator(model_fn=cnn_model_fn, model_dir="./signal_model/")

def get_radio_list(min, max):
    """
    Scan the radio frequency and return a list of frequency of
    fm stations.
    min: min frequency from user
    max: max frequency from user
    """
    print("recording signals...")
    data = []
    classify_list = []
    result_list = []
    scan_list = np.arange(min, max, 0.1)
    for frequency in scan_list:
        print("scanning " + str(frequency) + "...")
        data.append(read_frequency(frequency))
    print("start classifying signals...")
    all_data = np.vstack(data).astype(np.float32)
    pred_input_fn = tf.estimator.inputs.numpy_input_fn(x={"x": all_data},num_epochs=1,shuffle=False)
    pred_results = mnist_classifier.predict(input_fn=pred_input_fn)
    for i, result in enumerate(pred_results):
        print(i, result)
        if result['classes'] == 1:
            result_list.append(scan_list[i])
    return result_list
