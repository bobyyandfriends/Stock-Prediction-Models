import tensorflow as tf
import numpy as np
import time

def reducedimension(input_, dimension = 2, learning_rate = 0.01, hidden_layer = 256, epoch = 20):
    
    input_size = input_.shape[1]
    tf.compat.v1.disable_eager_execution()
    X = tf.compat.v1.placeholder("float", [None, input_size])
    
    weights = {
    'encoder_h1': tf.Variable(tf.random.normal([input_size, hidden_layer])),
    'encoder_h2': tf.Variable(tf.random.normal([hidden_layer, dimension])),
    'decoder_h1': tf.Variable(tf.random.normal([dimension, hidden_layer])),
    'decoder_h2': tf.Variable(tf.random.normal([hidden_layer, input_size])),
    }
    
    biases = {
    'encoder_b1': tf.Variable(tf.random.normal([hidden_layer])),
    'encoder_b2': tf.Variable(tf.random.normal([dimension])),
    'decoder_b1': tf.Variable(tf.random.normal([hidden_layer])),
    'decoder_b2': tf.Variable(tf.random.normal([input_size])),
    }
    
    first_layer_encoder = tf.nn.sigmoid(tf.add(tf.matmul(X, weights['encoder_h1']), biases['encoder_b1']))
    second_layer_encoder = tf.nn.sigmoid(tf.add(tf.matmul(first_layer_encoder, weights['encoder_h2']), biases['encoder_b2']))
    first_layer_decoder = tf.nn.sigmoid(tf.add(tf.matmul(second_layer_encoder, weights['decoder_h1']), biases['decoder_b1']))
    second_layer_decoder = tf.nn.sigmoid(tf.add(tf.matmul(first_layer_decoder, weights['decoder_h2']), biases['decoder_b2']))
    cost = tf.reduce_mean(input_tensor=tf.pow(X - second_layer_decoder, 2))
    optimizer = tf.compat.v1.train.RMSPropOptimizer(learning_rate).minimize(cost)
    sess = tf.compat.v1.InteractiveSession()
    sess.run(tf.compat.v1.global_variables_initializer())
    
    for i in range(epoch):
        last_time = time.time()
        _, loss = sess.run([optimizer, cost], feed_dict={X: input_})
        if (i + 1) % 10 == 0:
            print('epoch:', i + 1, 'loss:', loss, 'time:', time.time() - last_time)
        
    vectors = sess.run(second_layer_encoder, feed_dict={X: input_})
    tf.compat.v1.reset_default_graph()
    return vectors