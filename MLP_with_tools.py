# -*- coding: utf-8 -*-
"""
Created on Thu Sep 07 21:39:16 2017
Second course week 1 [S2W1], add tools for training
1,Data partation
2,Input Normalization
3,Regularization(L2,Drop out,Early stopping)
4,Exploding/vanishing avoidance
5,Gradient check   
@author: Gao
"""

import numpy as np
import pandas as pd 
class DataSet:
    def __init__(self,trn_set,trn_lb,tst_set = [],tst_lb=[]):
        self.training_set = trn_set
        self.training_label = trn_lb
        self.test_set = tst_set
        self.test_label = tst_lb
        self.train = {'data':[],'label':[]}
        self.dev = {'data':[],'label':[]}
        self.test = {}
        self.normalizeRange([0,1])
        #self.normalizeAll()
        
    def partition(self,partial):
        length = self.training_set.shape[1]
        len_of_train = int(length * partial)
        len_of_dev   = length - len_of_train
        self.train['data'] = self.training_set[:,:len_of_train]
        self.train['label'] = self.training_label[:len_of_train,:]
        self.dev['data'] = self.training_set[:,-len_of_dev:]
        self.dev['label'] = self.training_label[-len_of_dev:,:]
        
    def normalizeAll(self):
        metrix_X = self.training_set
        if len(self.test_set) != 0:
            metrix_X = np.concatenate((self.training_set,self.test_set),1)
        mean_X = np.sum(metrix_X,1)*1.0/metrix_X.shape[1]
        mean_X = mean_X.reshape(metrix_X.shape[0],1)
        metrix_X = metrix_X-mean_X
        sigma = np.sum(metrix_X**2,1)*1.0/metrix_X.shape[1]
        sigma = np.sqrt(sigma).reshape(metrix_X.shape[0],1)
        metrix_X = metrix_X/sigma
        self.training_set = metrix_X[:,:self.training_set.shape[1]]
        if len(self.test_set) != 0:
            self.test_set = metrix_X[:,-(self.test_set.shape[1]):]
            self.test['data'] = self.test_set
            self.test['label'] = self.test_label
            
    def normalizeRange(self,feature_list):
        metrix_X = self.training_set
        if len(self.test_set) != 0:
            metrix_X = np.concatenate((self.training_set,self.test_set),1)
        mean_X = np.sum(metrix_X,1)*1.0/metrix_X.shape[1]
        mean_X = mean_X.reshape(metrix_X.shape[0],1)
        metrix_X = metrix_X-mean_X
        sigma = np.sum(metrix_X**2,1)*1.0/metrix_X.shape[1]
        sigma = np.sqrt(sigma).reshape(metrix_X.shape[0],1)
        metrix_X = metrix_X/sigma
        self.training_set[feature_list,:] = metrix_X[feature_list,:self.training_set.shape[1]]
        if len(self.test_set) != 0:
            self.test_set = metrix_X[:,-(self.test_set.shape[1]):]
            self.test['data'] = self.test_set
            self.test['label'] = self.test_label
            
class NeuroLayer:
    def __init__(self,name,num_units,alpha):
        self.name = name
        self.num_units = num_units
        self.alpha = alpha
        self.weights = "nan"
        self.inputs = "nan"
        self.act = "nan"
        self.derivative_Z = "nan"
        self.delta = "nan"
        
    def activate(self,Z):
        A = 1.0/(1+np.exp(-Z))
        return A
        
    def computeA(self,input_x):
        assert(self.weights.shape[1] == input_x.shape[0])
        self.inputs = input_x
        z=np.dot(self.weights,input_x)
        self.act = self.activate(z)
        
    def computeDZ(self,input_delta):
        derivative_A_on_Z = self.act*(1-self.act) 
        assert(input_delta.shape == derivative_A_on_Z.shape)
        self.derivative_Z = input_delta*derivative_A_on_Z
        
    def computeLoss(self,input_y):
        self.derivative_Z = self.act - input_y.T
        
    def computeDelta(self):
        assert(self.weights.shape[0] == self.derivative_Z.shape[0])
        self.delta = np.dot(self.weights.T,self.derivative_Z)
        self.delta = np.delete(self.delta, (-1), axis=0)
        
    def updataWeights(self):
        DW = np.dot(self.derivative_Z,self.inputs.T)*1.0/self.inputs.shape[1]
        assert(DW.shape == self.weights.shape)
        self.weights = self.weights - self.alpha * DW
        
    def initParams(self,last_layer_units):
        self.weights = np.random.randn(self.num_units,last_layer_units+1)
        
    
class NeuroNet:
    def __init__(self, data):
        #train/test set is arranged by (num_of_feature, num_of_dataset)
        #train/test label is vertical vector, namey (num_of_dataset, 1)
        self.train_set = data.train['data']
        self.train_label = data.train['label']
        self.test_set = data.dev['data']
        self.test_label = data.dev['label']
        #useful while initialize the layers
        self.num_of_dataset = self.train_set.shape[1]
        self.num_of_feature = self.train_set.shape[0]
        self.layers = []
    def addLayer(self,name,num_units,alpha):
        layer = NeuroLayer(name,num_units,alpha)
        self.layers.append(layer)
        
    def initLayers(self):
        last_layer_units = self.num_of_feature
        for layer in self.layers:
            layer.initParams(last_layer_units)
            last_layer_units = layer.num_units
        
    def forward(self,input_x):
        #print "forward"
        feed_data = input_x
        for layer in self.layers:
            #add bias
            new_row = np.ones((1,feed_data.shape[1]))
            feed_data = np.row_stack((feed_data,new_row))
            layer.computeA(feed_data)
            feed_data = layer.act
    
    def backwark(self,input_y):
        layers = self.layers[::-1]
        delta = "nan"
        for layer in layers:
            if layer.name == "output":
                layer.computeLoss(input_y)
            else:
                layer.computeDZ(delta)
            layer.computeDelta()
            delta = layer.delta
            layer.updataWeights()
            
    def train(self,epoch_limits):
        print "training start..."
        for i in xrange(epoch_limits):
            self.forward(self.train_set)
            self.backwark(self.train_label)
            print("training %05d epoch: \n\tprecision on train %02.02f \n\tprecision on test  %02.02f"%(i+1,self.stats("train"),self.stats("test")))

            
    def stats(self,type_of_dataset):
        if type_of_dataset == "train":
            data = self.train_set
            label = self.train_label
        else:
            data = self.test_set
            label = self.test_label
        self.forward(data)
        layer = self.layers[-1]
        y = layer.act
        y[y >  0.5] = 1
        y[y <= 0.5] = 0
        return sum(y.T==label)*1.0/label.shape[0]
                
    def predict(self):
        self.forward(self.test_set)
        layer = self.layers[-1]
        y = layer.act
        y[y >  0.5] = 1
        y[y <= 0.5] = 0
        print y
        return sum(y.T==self.test_label)*1.0/self.test_label.shape[0],y            

def loadData():
    '''
    读取数据
    -- X为训练集，组织形式：每行一个样本，列个数即特征维度
    -- y为训练集标签，与训练集逐行对应
    -- Tx,Ty为测试集，同理
    '''
    train_set = pd.read_csv("X.csv",header=None)
    train_label = pd.read_csv("y.csv",header=None)
    test_set = pd.read_csv("Tx.csv",header=None)
    test_label = pd.read_csv("Ty.csv",header=None)
    data = DataSet(train_set.values.T,train_label.values,test_set.values.T,test_label.values)
    data.normalizeRange([0,1])
    data.partition(0.9)
    return data    
        
def buildNet():
    data = loadData()
    #根据课程内容，将数据集转置，调整成每列一个样本
    #标签集保持列向量形式
    net = NeuroNet(data)
    net.addLayer("first",100,0.01)
    net.addLayer("second",80,0.01)
    net.addLayer("third",60,0.01)
    net.addLayer("forth",40,0.01)
    net.addLayer("fifth",20,0.01)
    net.addLayer("output",1,0.01)
    net.initLayers()
    return net
    
def dothework():
    #创建神经网络
    net = buildNet()
    print("build success,net have %d layers"%len(net.layers))
    #迭代训练 5000次
    net.train(200000)
    net.stats('test')

if __name__ == "__main__":
    dothework()