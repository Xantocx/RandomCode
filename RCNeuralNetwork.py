import numpy as np

class NeuralNetwork:

	def __init__(self, layerSizes):
		weightShapes = [(a, b) for a, b in zip(layerSizes[1:], layerSizes[:-1])]

		self.__weights = [np.random.standard_normal(shape) / shape[1] ** 0.5 for shape in weightShapes]
		self.__biases = [np.zeros((shape, 1)) for shape in layerSizes[1:]]

	@staticmethod
	def activation(inputValue):
		return 1 / (1 + np.exp(-inputValue))

	@property
	def weights(self):
		return self.__weights
	
	@weights.setter
	def weights(self, weights):
		self.__weights = weights

	@property
	def biases(self):
		return self.__biases
	
	@biases.setter
	def biases(self, database):
		self.__biases = biases

	def calculate(self, inputVector):
		for weight, bias in zip(self.weights, self.biases):
			inputVector = self.activation(np.matmul(weight, inputVector) + bias)
		return inputVector

def main():
	layerSizes = (3, 5, 10)
	x = np.ones((layerSizes[0], 1))

	net = NeuralNetwork(layerSizes)
	prediction = net.calculate(x)

	print(prediction)

#main()
