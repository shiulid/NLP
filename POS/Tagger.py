import sys

import numpy as np
import math as m

from scipy.sparse import csr_matrix
from Data import LinearChainData

class Tagger(object):
    def __init__(self, average=True):
        self.useAveraging = average
        
    def ComputeThetaAverage(self):
        #self.thetaAverage = self.theta # change
        self.thetaAverage = self.theta - (self.thetaAverage/self.c)
        #TODO: Compute Average Parameters

    def PrintableSequence(self, sequence):
        return [self.train.tagVocab.GetWord(x) for x in sequence]

    def DumpParameters(self, outFile):
        fOut = open(outFile, 'w')
        sortedParams = (np.argsort(self.thetaAverage, axis=None)[::-1])[0:500]
        for i in sortedParams:
            (tag1ID, tag2ID, featureID) = np.unravel_index(i, self.theta.shape)
            fOut.write("%s %s %s %s\n" % (self.train.tagVocab.GetWord(tag1ID), self.train.tagVocab.GetWord(tag2ID), self.train.vocab.GetWord(featureID), self.thetaAverage[tag1ID,tag2ID,featureID]))
        fOut.close()

    def Train(self, nIter):
        self.c = 1
        self.thetaAverage = np.copy(self.theta)
        for i in range(nIter):
            nSent = 0
            flag = 1
            for (s,g) in self.train.featurizedSentences:
                c = self.c
                if len(g) <= 1:         #Skip any length 1 sentences - some numerical issues...
                    continue
                z = self.Viterbi(s, self.theta, len(g))
                if flag == 1:
                    if (np.array_equal(z , g) == False):
                        flag = 0
                sys.stderr.write("Iteration %s, sentence %s\n" % (i, nSent))
                sys.stderr.write("predicted:\t%s\ngold:\t\t%s\n" % (self.PrintableSequence(z), self.PrintableSequence(g)))
                #sys.stderr.write("predicted:\t%s\ngold:\t\t%s\n" % (z, g))
                nSent += 1
                self.UpdateTheta(s,g,z, self.theta, len(g),c, self.thetaAverage)
                self.c = self.c + 1
                
            if flag == 1:
                break
        
            
                
        if self.useAveraging:
            self.ComputeThetaAverage()

class ViterbiTagger(Tagger):
    def __init__(self, inFile, average=True):
        self.train = LinearChainData(inFile)
        self.useAveraging = average

        self.ntags    = self.train.tagVocab.GetVocabSize()
        self.theta    = np.zeros((self.ntags, self.ntags, self.train.vocab.GetVocabSize()))   #T^2 parameter vectors (arc-emission CRF)
        self.thetaSum = np.zeros((self.ntags, self.ntags, self.train.vocab.GetVocabSize()))   #T^2 parameter vectors (arc-emission CRF)
        self.nUpdates = 0

    def TagFile(self, testFile):
        self.test = LinearChainData(testFile, vocab=self.train.vocab)
        for i in range(len(self.test.sentences)):
            featurizedSentence = self.test.featurizedSentences[i][0]
            sentence = self.test.sentences[i]
            if self.useAveraging:
                v = self.Viterbi(featurizedSentence, self.thetaAverage, len(sentence))
            else:
                v = self.Viterbi(featurizedSentence, self.theta, len(sentence))
            words = [x[0] for x in sentence]
            tags  = self.PrintableSequence(v)
            for i in range(len(words)):
                print "%s\t%s" % (words[i], tags[i])
            print ""


    def Viterbi(self, featurizedSentence, theta, slen):
        """Viterbi"""
        #TODO: Implement the viterbi algorithm (with backpointers)

        if theta.any() == False:
            return [self.train.tagVocab.GetID('O') for x in range(featurizedSentence.shape[0])]

        ntags = self.ntags
        nwords = featurizedSentence.shape[0]
        tagsID = np.ones(nwords) * 2
        b = np.ones((ntags,nwords)) * 2

        PIprev = [featurizedSentence[0,:].dot(theta[t,0,:]) for t in range(ntags)]
        PI = np.zeros(ntags)
        for w in range(1,nwords):
            for t in range(1,ntags):
                pmax = featurizedSentence[w,:].dot(theta[t,2,:])+PIprev[2]
                tmax = 2
                for tp in range(1,ntags):
                    m = featurizedSentence[w,:].dot(theta[t,tp,:]) + PIprev[tp]
                    if ( m > pmax ):
                        pmax = m
                        tmax = tp
                PI[t] = pmax
                b[t,w] = tmax
            PIprev = np.copy(PI)

        tagsID[nwords - 1] = np.argmax(PI)
        for w in reversed(range(nwords-1)):
            tagsID[w] = b[tagsID[w+1],w+1]
  
        return tagsID


    #Structured Perceptron update
    def UpdateTheta(self, sentenceFeatures, 
                          goldSequence, 
                          viterbiSequence,
                          theta,
                          slen,
                            c,
                            thetaAverage):
        ntags = self.ntags
        START_TAG = self.train.tagVocab.GetID('START')
        nFeatures = self.train.vocab.GetVocabSize()

        if viterbiSequence[0] != goldSequence[0]:
            theta[goldSequence[0],START_TAG,:] = sentenceFeatures[0,:] + theta[goldSequence[0],START_TAG,:]
            theta[viterbiSequence[0],START_TAG] = theta[viterbiSequence[0],START_TAG,:] - sentenceFeatures[0,:]
            thetaAverage[goldSequence[0],START_TAG,:] = sentenceFeatures[0,:].multiply(c) + thetaAverage[goldSequence[0],START_TAG,:]
            thetaAverage[viterbiSequence[0],START_TAG] = thetaAverage[viterbiSequence[0],START_TAG,:] - sentenceFeatures[0,:].multiply(c)
            
        for i in range(1,slen):
            #TODO: update parameters if viterbiSequence[i] != goldSequence[i] or viterbiSequence[i-1] != goldSequence[i-1]
            if viterbiSequence[i] != goldSequence[i] or viterbiSequence[i-1] != goldSequence[i-1]:
                theta[goldSequence[i],goldSequence[i-1],:] = sentenceFeatures[i,:] + theta[goldSequence[i],goldSequence[i-1],:]
                theta[viterbiSequence[i],viterbiSequence[i-1]] = theta[viterbiSequence[i],viterbiSequence[i-1]] - sentenceFeatures[i,:]
                thetaAverage[goldSequence[i],goldSequence[i-1],:] = sentenceFeatures[i,:].multiply(c) + thetaAverage[goldSequence[i],goldSequence[i-1],:]
                thetaAverage[viterbiSequence[i],viterbiSequence[i-1]] = thetaAverage[viterbiSequence[i],viterbiSequence[i-1]] - sentenceFeatures[i,:].multiply(c)
                
                
