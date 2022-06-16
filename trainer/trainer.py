# For now this is just a copy of https://github.com/DonLuyendijk/Autocoureur

from sklearn.neural_network import MLPRegressor
import numpy as np
import matplotlib.pyplot as plt
import pickle

lines = np.loadtxt('default.samples')

inputs = lines[:, :-1]
outputs = lines[:, -1]

neural_net = MLPRegressor(
    max_iter = 600,
    hidden_layer_sizes = (50, 100, 100, 50),
    solver = 'adam',
    learning_rate_init = 0.001,
    n_iter_no_change = 50,
    verbose = True
).fit(inputs, outputs)

tests = [
    (inputs[i], outputs[i])
    for i in range(100, 1000)
]

for test in tests:
    print(f'prediction: {neural_net.predict([test[0]])}, target: {test[1]}')

print('score:', neural_net.score(inputs, outputs))

with open('neural_net', 'wb') as handle:
        pickle.dump(neural_net, handle)

plt.plot(neural_net.loss_curve_)
plt.show()
