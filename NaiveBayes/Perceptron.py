import sys

import numpy as np
from Eval import Eval

from imdb import IMDBdata

class Perceptron:
    def __init__(self, X, Y, N_ITERATIONS):
        self.N_ITERATIONS = N_ITERATIONS
        self.w = np.transpose(np.random.random(X.shape[1]))
        self.wAvg = np.copy(self.w)
        self.c = 1
        #TODO: Initalize parameters
        self.Train(X,Y)

    def ComputeAverageParameters(self):
        #TODO: Compute average parameters (do this part last)
        self.w = self.w - (self.wAvg/self.c)
        return

    def Train(self, X, Y):
        #TODO: Estimate perceptron parameters
        print "Training ... "
        w = self.w 
        wAvg = self.wAvg
        (nrow,ncol)=X.shape
        c = self.c
        for n in range(self.N_ITERATIONS):
            for doc in range(nrow):
                p = X[doc,:].dot(np.transpose(w))
                if p*Y[doc]<0:
                    if p>0:
                        p = 1
                    else:
                        p = -1
                    err = Y[doc]-p

                    indices = X.getrow(doc).indices
                    w[indices] = w[indices] + X[doc,indices].multiply(err)
                    wAvg[indices] = wAvg[indices] + X[doc,indices].multiply(c*err)
                    
                c = c + 1
            index = np.arange(X.shape[0])
            np.random.shuffle(index)
            X = X[index,:]
            Y = Y[index]
            print "Iteration# ",n
        self.c = c
        self.w = w
        self.wAvg = wAvg

        print "Training Complete !"        
        return

    def Predict(self, X):
        #TODO: Implement perceptron classification
        print "Predicting ..."
        Y=[]
        (nrow,ncol)=X.shape
        for doc in range(nrow):
            p = X[doc,:].dot(self.w)
            if p>0:
                Y.append(+1.0)
            else:
                Y.append(-1.0)
        return Y
    def Eval(self, X_test, Y_test):
        Y_pred = self.Predict(X_test)
        ev = Eval(Y_pred, Y_test)
        return ev.Accuracy()

    def PositiveWords(self,train):
        indices = list(reversed(np.argsort(self.w)))[0:20]
        Words = [train.vocab.GetWord(indices[x]) for x in range(20)]
        for word,weight in zip(Words,np.take(self.w,indices)):
            print word,weight
        return

    def NegativeWords(self,train):
        indices = list(np.argsort(self.w))[0:20]
        Words = [train.vocab.GetWord(indices[x]) for x in range(20)]
        for word,weight in zip(Words,np.take(self.w,indices)):
            print word,weight
        return
    

if __name__ == "__main__":
    print "Reading training data ..."
    train = IMDBdata("%s/train" % sys.argv[1])
    print "Reading test data ..."
    test  = IMDBdata("%s/test" % sys.argv[1], vocab=train.vocab)

    ptron = Perceptron(train.X, train.Y, int(sys.argv[2]))
    print ptron.Eval(test.X, test.Y)
    ptron.ComputeAverageParameters()
    print "Using Average Parameters ..."
    print ptron.Eval(test.X, test.Y)
    print "Iterations:",sys.argv[2]

    #TODO: Print out the 20 most positive and 20 most negative words
    print
    print "20 most positive words ..."
    ptron.PositiveWords(train)
    print
    print "20 most negative words ..."
    ptron.NegativeWords(train)



    
