import sys
import re
import os
import string
import subprocess
import json
from bs4 import BeautifulSoup
from bs4 import NavigableString
import urllib

def getNames():
    # Last Names
    Lnames = set()
    filename = "ner_data/dist.all.last"
    for line in open(filename):
        line = line.split(" ")
        Lnames.add(line[0].lower())
   
    # Female Names
    Fnames = set();
    filename = "ner_data/dist.female.first"
    for line in open(filename):
        line = line.split(" ")
        Fnames.add(line[0].lower())

    # Male Names
    Mnames = set();
    filename = "ner_data/dist.male.first"
    for line in open(filename):
        line = line.split(" ")
        Mnames.add(line[0].lower())

    # US Company Names
    r = urllib.urlopen("https://en.wikipedia.org/wiki/List_of_companies_of_the_United_States").read()
    soup = BeautifulSoup(r,"lxml")
    letters = soup.find_all("li",{"class":None,"id":None})
    Cnames = set()
    for line in letters:
        result = []
        for descendant in line.descendants:
            try:
                if isinstance(descendant, NavigableString):
                    result.append(descendant.decode("utf-8").strip())
                elif descendant.name == 'dl':
                    break
            except:
                continue
        name = u' '.join(result)
        Cnames.add(name.lower())
        if name == "Zynga":
            break
    
    # US Cities
    r = urllib.urlopen("https://simple.wikipedia.org/wiki/List_of_United_States_cities_by_population").read()
    soup = BeautifulSoup(r,"lxml")
    letters = soup.find_all("table",{"class":"wikitable sortable"})
    letters = letters[0].findAll('td',{"align":None})
    Pnames = set()
    for line in letters:
        result = []
        for descendant in line.descendants:
            try:
                if isinstance(descendant, NavigableString):
                    result.append(descendant.decode("utf-8").strip())
                elif descendant.name == 'dl':
                    break
            except:
                continue
        name = u' '.join(result)
        if name.lower() not in Pnames:
            Pnames.add(name.lower())
    
    # Restaurants
    r = urllib.urlopen("https://en.wikipedia.org/wiki/List_of_restaurant_chains_in_the_United_States").read()
    soup = BeautifulSoup(r,"lxml")
    letters = soup.find_all("table",{"class":"wikitable sortable"})
    letters = letters[0].findAll("tr")
    Rnames = set()
    i = 0
    for i in range(1,281):
        line = letters[i].find("td")
        result = []
        for descendant in line.descendants:  
            try:
                if isinstance(descendant, NavigableString):
                    result.append(descendant.decode("utf-8").strip())
                elif descendant.name == 'dl':
                    break
            except:
                continue
        name = u' '.join(result)
        if name=="":
            continue
        if name.lower() not in Rnames:
            Rnames.add(name.lower())
       
    names12 = set(["january","february","march","april","may","june","july","august","september","october","november","december"])
    names = Lnames | Fnames
    names |= Mnames
    names |= Cnames
    names |= Pnames
    names |= names12
    names |= Rnames
    return names

names = getNames()
tagDict = {}
for line in open('tagDict'):
    (word, tag) = line.strip().split()
    tagDict[word] = tag

wordClusters = {}
for line in open('60K_clusters.bits.txt'):
    (cluster, word) = line.strip().split()
    wordClusters[word] = []
    for b in [4,8,12]:
        wordClusters[word].append(cluster[0:b])

def GetFeatures(word):
    features = []

    if tagDict.has_key(word):
        features.append("tagDict=%s" % tagDict[word])

    if wordClusters.has_key(word):
        for c in wordClusters[word]:
            features.append("cluster=%s" % c)

    features.append("word=%s" % word)
    features.append("word_lower=%s" % word.lower())
    if(len(word) >= 4):
        features.append("prefix=%s" % word[0:1].lower())
        features.append("prefix=%s" % word[0:2].lower())
        features.append("prefix=%s" % word[0:3].lower())
        features.append("suffix=%s" % word[len(word)-1:len(word)].lower())
        features.append("suffix=%s" % word[len(word)-2:len(word)].lower())
        features.append("suffix=%s" % word[len(word)-3:len(word)].lower())

    if re.search(r'^[A-Z]', word):
        features.append('INITCAP')
    if re.match(r'^[A-Z]+$', word):
        features.append('ALLCAP')
    if re.match(r'.*[0-9].*', word):
        features.append('HASDIGIT')
    if re.match(r'.*[.,;:?!-+\'"].*', word):
        features.append('HASPUNCT')
    if word.lower() in names:
        features.append('NAME')
    return features

class FeatureExtractor:
    def Extract(self, words, i):
        features = GetFeatures(words[i])
        return features
