# Word's most frequent tag baseline
import numpy as np
from Data import Data
from Data import LinearChainData

trainFile = "data/twitter_train_universal.txt"
data = Data(trainFile).data;

testFile = "data/twitter_test_universal.txt"

train = LinearChainData(trainFile)

d = {}
for l in data:
    for (word,tag) in l: 
        word = word.lower()
        t = np.zeros(train.tagVocab.GetVocabSize())
        t[train.tagVocab.GetID(tag)-1] = 1
        if word in d:
            d[word] += d[word] + t
        else:
            d[word] = t
            
for word in d:
    d[word] = np.argmax(d[word])

 
        
test = LinearChainData(testFile,train.vocab)
for i in range(len(test.sentences)):
    featurizedSentence = test.featurizedSentences[i][0]
    sentence = test.sentences[i]

    words = [x[0] for x in sentence]
    v = np.zeros(len(words))
    for i in range(len(words)):
        if words[i] in d:
            v[i] = d[words[i]] + 1
        else:
            v[i] = train.tagVocab.GetID('NOUN')

    tags = [train.tagVocab.GetWord(x) for x in v]
    for i in range(len(words)):
        print "%s\t%s" % (words[i], tags[i])
    print "" 





