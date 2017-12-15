import tensorflow as tf
import numpy as np
def case1():
    dx = np.float32(np.random.rand(2, 100))
    dy = np.dot([0.100, 0.200], dx) + 0.300
    b = tf.Variable(tf.zeros([1]))
    W = tf.Variable(tf.random_uniform([1, 2], -1.0, 1.0))
    y = tf.matmul(W, dx) + b
    
    loss = tf.reduce_mean(tf.square(y - dy))
    optimizer = tf.train.GradientDescentOptimizer(0.5)
    train = optimizer.minimize(loss)
    init = tf.global_variables_initializer()
    sess = tf.Session()
    sess.run(init)
    for step in range(0, 201):
        sess.run(train)
        if step % 20 == 0:
            print ( step, sess.run(W), sess.run(b) )
            
def mnist():
    import input_data
    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
    x = tf.placeholder("float", [None, 784])
    W = tf.Variable(tf.zeros([784,10]))
    b = tf.Variable(tf.zeros([10]))    
    y = tf.nn.softmax(tf.matmul(x,W) + b)
    y_ = tf.placeholder("float", [None,10])
    cross_entropy = -tf.reduce_sum(y_*tf.log(y))
    train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)
    init = tf.global_variables_initializer()
    sess = tf.Session()
    sess.run(init)
    for i in range(1000):
        batch_xs, batch_ys = mnist.train.next_batch(100)
        sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})    
    correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    print ( sess.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}) )
if __name__ == "__main__":
    #case1()
    mnist()