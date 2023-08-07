import numpy as np
import matplotlib.pyplot as plt

plt.style.use('./deeplearning.mplstyle')
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from lab_utils_common import dlc
from lab_coffee_utils import load_coffee_data, plt_roast, plt_prob, plt_layer, plt_network, plt_output_unit
import logging

logging.getLogger("tensorflow").setLevel(logging.ERROR)
tf.autograph.set_verbosity(0)

# Defining the dataset
X, Y = load_coffee_data()
print(X.shape, Y.shape)

# Plot the dataset
plt_roast(X, Y)

# Normalize the data
print(f"Temperature Max, Min pre normalization: {np.max(X[:, 0]):0.2f}, {np.min(X[:, 0]):0.2f}")
print(f"Duration    Max, Min pre normalization: {np.max(X[:, 1]):0.2f}, {np.min(X[:, 1]):0.2f}")
norm_l = tf.keras.layers.Normalization(axis=-1)
norm_l.adapt(X)  # learns mean, variance
Xn = norm_l(X)
print(f"Temperature Max, Min post normalization: {np.max(Xn[:, 0]):0.2f}, {np.min(Xn[:, 0]):0.2f}")
print(f"Duration    Max, Min post normalization: {np.max(Xn[:, 1]):0.2f}, {np.min(Xn[:, 1]):0.2f}")

# Tile/copy our data to increase the training set size and reduce the number of training epochs
Xt = np.tile(Xn, (1000, 1))
Yt = np.tile(Y, (1000, 1))
print(Xt.shape, Yt.shape)

# Defining the model
tf.random.set_seed(1234)  # applied to achieve consistent results
model = Sequential(
    [
        tf.keras.Input(shape=(2,)),
        Dense(3, activation='sigmoid', name='layer1'),
        Dense(1, activation='sigmoid', name='layer2')
    ]
)

# Description of network
model.summary()

# Parameter counts - correspond to the number of elements in the weight and bias arrays as shown below
L1_num_params = 2 * 3 + 3  # W1 parameters  + b1 parameters
L2_num_params = 3 * 1 + 1  # W2 parameters  + b2 parameters
print("L1 params = ", L1_num_params, ", L2 params = ", L2_num_params)

# In the first layer with 3 units, we expect W to have a size of (2,3) and 𝑏 should have 3 elements.
# In the second layer with 1 unit, we expect W to have a size of (3,1) and 𝑏 should have 1 element
W1, b1 = model.get_layer("layer1").get_weights()
W2, b2 = model.get_layer("layer2").get_weights()
print(f"W1{W1.shape}:\n", W1, f"\nb1{b1.shape}:", b1)
print(f"W2{W2.shape}:\n", W2, f"\nb2{b2.shape}:", b2)

# The model.compile statement defines a loss function and specifies a compile optimization.
model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(),
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
)

# The model.fit statement runs gradient descent and fits the weights to the data.
model.fit(
    Xt, Yt,
    epochs=10,
)
# In the compile statement above, the number of epochs was set to 10.
# This specifies that the entire data set should be applied during training 10 times.

# Updated weights
W1, b1 = model.get_layer("layer1").get_weights()
W2, b2 = model.get_layer("layer2").get_weights()
print("W1:\n", W1, "\nb1:", b1)
print("W2:\n", W2, "\nb2:", b2)

'''
Next, we will load some saved weights from a previous training run. This is so that this notebook remains robust to 
changes in Tensorflow over time. Different training runs can produce somewhat different results and the discussion below 
applies to a particular solution. Feel free to re-run the notebook with this cell commented out to see the difference.
'''

W1 = np.array([
    [-8.94, 0.29, 12.89],
    [-0.17, -7.34, 10.79]])
b1 = np.array([-9.87, -9.28, 1.01])
W2 = np.array([
    [-31.38],
    [-27.86],
    [-32.79]])
b2 = np.array([15.54])
model.get_layer("layer1").set_weights([W1, b1])
model.get_layer("layer2").set_weights([W2, b2])

# Input data
X_test = np.array([
    [200, 13.9],  # postive example
    [200, 17]])  # negative example
X_testn = norm_l(X_test)
predictions = model.predict(X_testn)
print("predictions = \n", predictions)

# To convert the probabilities to a decision, we apply a threshold:
yhat = np.zeros_like(predictions)
for i in range(len(predictions)):
    if predictions[i] >= 0.5:
        yhat[i] = 1
    else:
        yhat[i] = 0
print(f"decisions = \n{yhat}")

yhat = (predictions >= 0.5).astype(int)
print(f"decisions = \n{yhat}")

# Layer functions
plt_layer(X, Y.reshape(-1, ), W1, b1, norm_l)

plt_output_unit(W2, b2)

netf = lambda x: model.predict(norm_l(x))
plt_network(X, Y, netf)
