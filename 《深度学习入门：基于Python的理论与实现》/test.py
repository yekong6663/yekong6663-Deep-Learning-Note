import numpy as np
#激活函数
def sigmoid(x):
  return 1/(1+np.exp(-x))
def IdentifyFunction(x):
  return x
#初始化所有权重、偏置
def InitNetwork():
  network = {}
  network["W1"] = np.array([[0.1, 0.3, 0.5], [0.2, 0.4, 0.6]])
  network["W2"] = np.array([[0.1, 0.4], [0.2, 0.5], [0.3, 0.6]])
  network["W3"] = np.array([[0.1, 0.3], [0.2, 0.4]])
  network["B1"] = np.array([0.1, 0.2, 0.3])
  network["B2"] = np.array([0.1, 0.2])
  network["B3"] = np.array([0.1, 0.2])

  return network
#进行神经网络运算
def Forward(network,x):
  A1 = np.dot(x,network["W1"]) + network["B1"]
  Z1 = sigmoid(A1)
  A2 = np.dot(Z1,network["W2"]) + network["B2"]
  Z2 = sigmoid(A2)
  A3 = np.dot(Z2,network["W3"]) + network["B3"]
  Z3 = IdentifyFunction(A3)
  return Z3

network = InitNetwork()
x = np.array([1.0, 0.5])
y = Forward(network, x)
print(y)