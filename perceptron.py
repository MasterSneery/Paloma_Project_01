import numpy as np

# Definir la función de activación del perceptrón
def activation_function(x):
    if x >= 0:
        return 1
    else:
        return 0

# Definir la función de entrenamiento del perceptrón
def train_perceptron(X, y, learning_rate=0.1, epochs=10):
    # Agregar una columna de unos a los datos de entrada para el término de sesgo
    X = np.insert(X, 0, 1, axis=1)

    # Inicializar los pesos aleatoriamente
    weights = np.random.randn(X.shape[1])

    for epoch in range(epochs):
        for i in range(len(X)):
            # Calcular el producto punto de los pesos y las entradas
            h = np.dot(X[i], weights)

            # Aplicar la función de activación
            y_pred = activation_function(h)

            # Actualizar los pesos
            weights += learning_rate * (y[i] - y_pred) * X[i]

    return weights

# Definir la función de prueba del perceptrón
def test_perceptron(X, weights):
    # Agregar una columna de unos a los datos de entrada para el término de sesgo
    X = np.insert(X, 0, 1, axis=1)

    # Calcular el producto punto de los pesos y las entradas
    h = np.dot(X, weights)

    # Aplicar la función de activación
    y_pred = np.array([activation_function(x) for x in h])

    return y_pred

# Definir los datos de entrenamiento y prueba
X_train_and = np.array([[0,0], [0,1], [1,0], [1,1]])
y_train_and = np.array([0, 0, 0, 1])

X_train_or = np.array([[0,0], [0,1], [1,0], [1,1]])
y_train_or = np.array([0, 1, 1, 1])

X_train_not = np.array([[0], [1]])
y_train_not = np.array([1, 0])

# Entrenar el perceptrón para la compuerta AND
weights_and = train_perceptron(X_train_and, y_train_and)

# Entrenar el perceptrón para la compuerta OR
weights_or = train_perceptron(X_train_or, y_train_or)

# Entrenar el perceptrón para la compuerta NOT
weights_not = train_perceptron(X_train_not, y_train_not)

# Probar el perceptrón para la compuerta AND
X_test_and = X_train_and
y_pred_and = test_perceptron(X_test_and, weights_and)

# Probar el perceptrón para la compuerta OR
X_test_or = X_train_or
y_pred_or = test_perceptron(X_test_or, weights_or)

# Probar el perceptrón para la compuerta NOT
X_test_not = X_train_not
y_pred_not = test_perceptron(X_test_not, weights_not)

# Imprimir los resultados
print("AND")
print("Entradas:", X_test_and)
print("Salidas deseadas:", y_train_and)
print("Salidas predichas:", y_pred_and)

print("OR")
print("Entradas:", X_test_or)
print("Salidas deseadas:", y_train_or)
print("Salidas predichas:", y_pred_or)

print("NOT")
print("Entradas:", X_test_not)
print("Salidas deseadas:",y_train_not)
print("Salidas predichas:",y_pred_not)