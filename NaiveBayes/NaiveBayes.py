import sys

import numpy as np
from Eval import Eval
import math as m

from imdb import IMDBdata
from scipy.sparse import csc_matrix

class NaiveBayes:
    def __init__(self, X, Y, ALPHA=1.0):
        self.ALPHA=float(ALPHA)
        #TODO: Initalize parameters
        self.Train(X,Y)

    def Train(self, X, Y):
        #TODO: Estimate Naive Bayes model parameters
        #<Not keeping a count of positive and negative documents since both are equal>
        print "Training ..."
        #Get count(wordId,pos/neg) for each
        (nrow,ncol) = X.shape
        countP = np.array(X[Y == 1,:].sum(axis=0)).flatten()
        countN = np.array(X[Y==-1,:].sum(axis=0)).flatten()
        
        V = ncol
        denP = sum(countP) + (self.ALPHA*V)
        denN = sum(countN) + (self.ALPHA*V)

        self.LogProbP = np.log10(np.maximum(1,countP)) + m.log10(self.ALPHA) - m.log10(denP)
        self.LogProbN = np.log10(np.maximum(1,countN)) + m.log10(self.ALPHA) - m.log10(denN)
        self.LogProbUNKp = m.log10(self.ALPHA)- m.log10(denP)
        self.LogProbUNKn = m.log10(self.ALPHA)- m.log10(denN)
        
        print "Training Completed! "
        return

    def Predict(self, X):
        #TODO: Implement Naive Bayes Classification
        ########not considering words not in training vocab
        print "Predicting ..."
        Y = []
        (nrow,ncol) = X.shape
        LogProbP = self.LogProbP
        LogProbN = self.LogProbN
        LogProbUNKp = self.LogProbUNKp
        LogProbUNKn = self.LogProbUNKn

        for doc in range(nrow):
            LogP = X[doc,:].dot(LogProbP)
            LogN = X[doc,:].dot(LogProbN)
            
            if LogP>LogN:
                Y.append(+1.0)
            else:
                Y.append(-1.0)
            
        return Y

    def Eval(self, X_test, Y_test):
        Y_pred = self.Predict(X_test)
        ev = Eval(Y_pred, Y_test)
        return ev.Accuracy()

if __name__ == "__main__":
    print "Reading training data ... "
    train = IMDBdata("%s/train" % sys.argv[1])
    print "Reading test data ..."
    test  = IMDBdata("%s/test" % sys.argv[1], vocab=train.vocab)
    nb = NaiveBayes(train.X, train.Y, float(sys.argv[2]))
    print nb.Eval(test.X, test.Y)
    print "ALPHA:",float(sys.argv[2])
