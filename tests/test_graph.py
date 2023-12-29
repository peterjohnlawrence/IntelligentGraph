import intelligentgraph
from intelligentgraph import IntelligentConjunctiveGraph, IntelligentDataset,IntelligentGraph,SCRIPT
from rdflib import  Literal,   URIRef
from rdflib.namespace import FOAF
from datetime import date

def test_simpleLiteral():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")
    g.add((ig, FOAF.birthday, Literal('''_result= 1952 
    ''',datatype=SCRIPT.python)))

    for triple in g.triples( (None , None, None)):
        assert triple[0]==URIRef("http://inova8.com/ig")
        assert triple[1]==FOAF.birthday
        assert triple[2].toPython() ==1952

def test_simpleLiteralwoIntelligence():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")
    g.add((ig, FOAF.birthday, Literal('1952',datatype=SCRIPT.python)))
    g.disableIntelligence()
    for triple in g.triples( (None , None, None)):
        assert triple[0]==URIRef("http://inova8.com/ig")
        assert triple[1]==FOAF.birthday
        assert triple[2] ==Literal('1952',datatype=SCRIPT.python)

def test_simpleDatetime():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")
    g.add((ig, FOAF.birthday, Literal('''from datetime import date
_result =date(1951, 3, 8) 
    ''',datatype=SCRIPT.python)))
    for triple in g.triples( (None , None, None)):
        assert triple[0]==URIRef("http://inova8.com/ig")
        assert triple[1]==FOAF.birthday
        assert triple[2].toPython() == date(1951, 3, 8)


def test_AgeCalc():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")

    g.add((ig, FOAF.birthday, Literal('''from datetime import date
_result =date(1951, 3, 8) 
    ''',datatype=SCRIPT.python)))
    
    g.add((ig, FOAF.age, Literal('''
from rdflib.namespace import FOAF
from datetime import date
for triple in g.triples( (s , FOAF.birthday, None)):
    age= int((date.today()-triple[2].toPython()).days/365.25)
    _result = age''',datatype=SCRIPT.python)))

    for triple in g.triples( (None , FOAF, None)):
        assert triple[0]==URIRef("http://inova8.com/ig")
        assert triple[1]==FOAF.age 
        assert triple[2].toPython() == 72

def test_externalData():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")
    g.add((ig, FOAF.knows, Literal('''
import requests
from rdflib.namespace import FOAF 
def getKnows(individual):
  response = requests.get("https://random-word-api.herokuapp.com/word?lang=en&number=5")
  for word in response.json():
    yield (individual, FOAF.knows, URIRef("http://inova8.com/"+word))
_result = getKnows(s)''',datatype=SCRIPT.python)))

    for row in g.query( '''select (count(*) as ?total)where{?s ?p ?o}'''):
        assert row['total'].toPython()==5

def test_scriptRecursion():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")
    g.add((ig, FOAF.birthday, Literal('''
_result = Literal("_result =1952" ,datatype=SCRIPT.python)
    ''',datatype=SCRIPT.python)))

    for triple in g.triples( (None , None, None)):
        #assert triple[0]==URIRef("http://inova8.com/ig")
        #assert triple[1]==FOAF.birthday
        print(triple[2])
        assert triple[2].toPython()==1952

def test_circularReference():
    g = IntelligentGraph()
    ig = URIRef("http://inova8.com/ig")
    ig1 = URIRef("http://inova8.com/ig1")
    ig2 = URIRef("http://inova8.com/ig2")
    ig3 = URIRef("http://inova8.com/ig3")
    ig4 = URIRef("http://inova8.com/ig4")
    g.add((ig, ig1, Literal('''
from rdflib.namespace import FOAF
for triple in g.triples( (s , URIRef("http://inova8.com/ig2"), None)):
    o= triple[2]
    _result = o''',datatype=SCRIPT.python)))
    g.add((ig, ig2, Literal('''
from rdflib.namespace import FOAF
for triple in g.triples( (s , URIRef("http://inova8.com/ig3"), None)):
    o= triple[2]
    _result = o''',datatype=SCRIPT.python)))
    g.add((ig, ig3, Literal('''
from rdflib.namespace import FOAF
for triple in g.triples( (s , URIRef("http://inova8.com/ig4"), None)):
    o= triple[2]
    _result = o''',datatype=SCRIPT.python)))
    g.add((ig, ig4, Literal('''
from rdflib.namespace import FOAF
for triple in g.triples( (s , URIRef("http://inova8.com/ig1"), None)):
    o= triple[2]
    _result = o''',datatype=SCRIPT.python)))
    for triple in g.triples( (ig, ig1, None)):
        print(triple[2])
        assert triple[2]==Literal("Error=Script circular reference", datatype=SCRIPT.error)