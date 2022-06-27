from sklearn.neural_network import MLPRegressor
import numpy as np
import pickle

lines = np.loadtxt('default.samples')

inputs = lines[:, :-1]
outputs = lines[:, -1]

network = MLPRegressor(
    max_iter = 600,
    hidden_layer_sizes = (120),
    alpha = 4,
    solver = 'adam',
    learning_rate_init = 0.001,
    n_iter_no_change = 50,
    verbose = True
).fit(inputs, outputs)

tests = [ (inputs[i], outputs[i]) for i in range(0, 5000, 50) ]
for test in tests:
    print(f'Predication: {network.predict([test[0]])}, Answer: {test[1]}')

print(f'Score: {network.score(inputs, outputs)}')

with open('../simulation/control_client/neural_network_func', 'wb') as handle:
    pickle.dump(network, handle)
