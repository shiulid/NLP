from bs4 import BeautifulSoup
from bs4 import NavigableString
import urllib

def getNames():
    Lnames = set()
    filename = "ner_data/dist.all.last"
    for line in open(filename):
        line = line.split(" ")
        Lnames.add(line[0].lower())
   

    Fnames = set();
    filename = "ner_data/dist.female.first"
    for line in open(filename):
        line = line.split(" ")
        Fnames.add(line[0].lower())


    Mnames = set();
    filename = "ner_data/dist.male.first"
    for line in open(filename):
        line = line.split(" ")
        Mnames.add(line[0])
 
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
        print name
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

    

    
        


    
    


    

