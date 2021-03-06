
from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf


print("Ivanl00001-----")
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

x = tf.placeholder(tf.float32, [None, 784])
W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))

y = tf.nn.softmax(tf.matmul(x, W) + b)

# 这里计算交叉熵
y_ = tf.placeholder("float", [None,10])
cross_entropy = -tf.reduce_sum(y*tf.log(y))


train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)
init = tf.initialize_all_variables()

session = tf.Session()
session.run(init)

for i in range(1000):
    batch_xs, batch_ys = mnist.train.next_batch(100)
    session.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
print(session.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}))


print("ivanl001-------end")




