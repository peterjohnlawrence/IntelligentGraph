![](IntelligentGraph.gif)
# IntelligentGraph
Python package that adds IntelligentGraph capabilities to RDFLib RDF graph package.

IntelligentGraph introduces a special Literal value: a SCRIPT. These literals have a datatype of SCRIPT.python.
When a SCRIPT-valued object is retrieved from the RDF store, the script is executed and the values returned from the execution of the script replace the SCRIPT-valued object.

# Documentation

Most of the documentation for IntelligentGraph can be found in RDFlib, see https://rdflib.readthedocs.io for its documentation built from the code. 

# Table of Contents
1. [Installation](#installation)
2. [Getting Started](#getting_started)
    1. [Really simple start](#really_simple_start)
    2. [Let's get a bit more real](#lets_get_a_bit_more_real)
    3. [Fetching External Data ](#fetching_external_data)
    4. [Summary](#summary)
4. [Script Writing](#script_writing)
5. [Controlling Intelligence](#controlling_intelligence)
6. [What Next?](#what_next)
   1. [Data Analysis](#data_analysis)
   2. [Integraion with IoT and IIoT](#integration_with_iot_and_iiot)
   3. [Integration with Large Language Models (LLMs)](#integration_with_large_language_models_llms)  
8. [Caveats](#caveats)

# Installation <a name="installation"></a>
The latest release of RDFLib may be installed with Python's package management tool pip. 
Since IntelligentGraph depends on rdflib, version >7 of rdflib will be installed.
However, since IntelligentGraph is still experimental it is loaded directly from GitHub
```python
$ pip install "git+https://github.com/peterjohnlawrence/IntelligentGraph.git"
```
Jupyter or Google Colab is a handy way of interacting with graphs. To install from within a cell
```python
!pip install "git+https://github.com/peterjohnlawrence/IntelligentGraph.git"
```
# Getting Started <a name="getting_started"></a>

IntelligentGraph follows the same pattern as RDFLib, since IntelligentGraph is derived from Graph. So everything that works for RDFLib works the same for IntelligentGraph.

## Really simple start  <a name="really_simple_start"></a>

The simplest example is to create an IntelkligentGraph with a single triple, whose value is a script that returns a literal. the value is return by assigning it to the predefined _result variable. We don't need a script to do this, but let's build up simply:
```python
from  intelligentgraph import IntelligentGraph,SCRIPT
from rdflib import  Literal,   URIRef
from rdflib.namespace import FOAF
from datetime import date

g = IntelligentGraph()
iggy = URIRef("http://inova8.com/iggy")
g.add((iggy, FOAF.birthday, Literal(date(1951, 3, 8))))
```
We can query this graph (with one triple!) as follows:
```python
for triple in g.triples( (None , None, None)):
    print(triple)
```
This returns the single triple result: subject, predicate, object
```python
(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/birthday'), rdflib.term.Literal('1951-03-08', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date')))
```
Note that the object's script value has been replaced with a literal containing the xsd:date value that was returned from the script when it was evaluated.

## Let's get a bit more real <a name="lets_get_a_bit_more_real"></a>

If we wanted to know a person's age, we could of course query this graph, and as part of the SPARQL query, or Python code handling the returned values, calculate the age in years. For example 
```python
s = URIRef("http://inova8.com/ig")
from rdflib.namespace import FOAF
from datetime import date
for triple in g.triples( (s , FOAF.birthday, None)):
    age= int((date.today()-triple[2].toPython()).days/365.25)
    print (age)
```
The result of which is:
```python
72
```
However, if we were to share the graph with someone, they would not have access to this code unless we shared that as well. Why not incorporate the age calculation *within* the graph? This is analogous to a spreadsheet in which some cell values are literals whilst others are calculations based on other cell values.
Let's add a calculation script for the FOAF:age as follows. 
Note that the script will be initialized with values as follows:
- The value 's' is supplied to the script as the subject of the triple with which the script is associated as the object. 
- The predicate of the same triples is supplied a variable 'p'.
- If we are using 'quads' then the context is provided as variable 'ctx'.
- Finally, the graph within which the triple is defined is provided as variable 'g'


```python
g.add((ig, FOAF.age, Literal('''
from rdflib.namespace import FOAF
from datetime import date
for triple in g.triples( (s , FOAF.birthday, None)):
    age= int((date.today()-triple[2].toPython()).days/365.25)
    _result = age''',datatype=SCRIPT.python)))
```
We can view the calculated graph  using
```python
print(g.serialize(format="n3"))
```
Which returns the following graph in n3 format. Again, please note that the scripts have been replaced by their calculated equivalent.
```python
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
<http://inova8.com/ig> foaf:age 72 ;
    foaf:birthday "1951-03-08"^^xsd:date .\n\n
```

## Fetching External Data <a name="fetching_external_data"></a>

There are many occasions when we want to merge a graph with external information. Usually, this is done by running some code that retrieves the triples from the external data source, such as an IoT server. This data then has to be merged with the underlying graph.
IntelligentGraph offers a better alternative: add an agent *within* the graph that pulls this external data just-in-time, instead of just-in-case.

Let's start by simulating an external service that returns the FOAF:knows triples about a particular individual. In reality, we will use an external service (https://random-word-api.herokuapp.com) that generates random names.
```python
s = URIRef("http://inova8.com/ig")
import requests
def getKnows(individual):
  response = requests.get("https://random-word-api.herokuapp.com/word?lang=en&number=5") 
  for word in response.json():
    yield (individual, FOAF.knows, URIRef("http://inova8.com/"+word))
for triple in getKnows(s):
  print(triple)
```
If we were to run this outside of the graph, it would return triples something like this (remember the values are random):
```python
(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.URIRef('http://inova8.com/sandpapery'))
(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.URIRef('http://inova8.com/trimotors'))
(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.URIRef('http://inova8.com/apostrophe'))
(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.URIRef('http://inova8.com/flyspecking'))
(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.URIRef('http://inova8.com/grooving'))
```
Instead of merging these two graphs, let's add an agent script that returns these results. we use the 'yield' pattern so that a script need not fetch all results. Instead, yield allows each value to be fetced on request:
```python
g.add((ig, FOAF.knows, Literal('''
import requests
def getKnows(individual):
  response = requests.get("https://random-word-api.herokuapp.com/word?lang=en&number=5") 
  for word in response.json():
    yield (individual, FOAF.knows, URIRef("http://inova8.com/"+word)) 
_result = getKnows(s)''',datatype=SCRIPT.python)))
```
We can again view the entire graph simply by serializing it as follows:
```python
print(g.serialize(format="n3"))
```
```python
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://inova8.com/ig> foaf:age 72 ;
    foaf:birthday "1951-03-08"^^xsd:date ;
    foaf:knows <http://inova8.com/anthodium>,
        <http://inova8.com/batts>,
        <http://inova8.com/exodermises>,
        <http://inova8.com/fascicled>,
        <http://inova8.com/hangers> .
```
## Summary <a name="summary"></a>

In this example, the asserted graph only contains three statements, each of which  has a script for an object value:
```python
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
<http://inova8.com/ig>
    foaf:birthday """from datetime import date
                _result =date(1951, 3, 8)"""^^<http://inova8.com/script/python> ;
    foaf:age """
                from rdflib.namespace import FOAF
                from datetime import date
                for triple in g.triples( (s , FOAF.birthday, None)):
                age= int((date.today()-triple[2].toPython()).days/365.25)
                _result = age"""^^<http://inova8.com/script/python> ;

    foaf:knows """
                import requests
                def getKnows(individual):
                    response = requests.get("https://random-word-api.herokuapp.com/word?lang=en&number=5")
                    for word in response.json():
                        yield (individual, FOAF.knows, URIRef("http://inova8.com/"+word)) 
                _result = getKnows(s)"""^^<http://inova8.com/script/python> .
```
When queried as an IntelligentGraph, it will appear that the graph contains the following:
```python
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://inova8.com/ig> foaf:age 72 ;
    foaf:birthday "1951-03-08"^^xsd:date ;
    foaf:knows <http://inova8.com/anthodium>,
        <http://inova8.com/batts>,
        <http://inova8.com/exodermises>,
        <http://inova8.com/fascicled>,
        <http://inova8.com/hangers> .
```
# Script Writing <a name="script_writing"></a>

Scripts are any valid Python. 

Context is provided to each script in the form of the following variables:

- g: The IntelligentGraph object that contains the triples (or quads). This object can be  
- s: The subject node of the triple 
- p: The predicate node of the triple
- o: The object node of the triple. This node is a literal containing the script.
- ctx: the context of the triple. In the case of a conjunctive graph or dataset, it is the particular graph dataset that contains the triple.

The result of the script is returned by assigning the value to _result.
The _result value can be any of the following types:
- A Python scalar, which will be converted to a corresponding literal scalar
- A RDFLib Literal
- A RDFLib URIRef
- A triple
- A set of triples, using a generator that yields each triple when requested.

# Controlling Intelligence <a name="controlling_intelligence"></a>

The capabilities of an IntelligentGraph to evaluate a script can be disabled with

- IntelligentGraph.disableIntelligence()

After which the IntelligentGraph behaves as a 'normal' RDFLib Graph. RTghis is useful if one wants to, say, serialize the graph.

Intelligence (aka evaluation of scripts) is reenabled with:

- IntelligentGraph.enableIntelligence()

 To check if an IntelligentGraph has intelligence enabled use:

- IntelligentGrapg.isEnabled()

# What Next? <a name="what_next"></a>
IntelligentGraph opens up all sorts of data analysis capabilities which can now become agents within the graph rather than external code.

## Data Analysis <a name="data_analysis"></a>

Often data analysis is done within a spreadsheet because it is so easy to add calculated columns, as well as aggregate column values. This can be performed just as easily within the IntelligentGraph:

- Each class is another spreadsheet.
- Consider each instance of that class or 'entity', aka subject of a triple, as the identity of the row.
- Each property of the entity then becomes another column.
- Aggregations are the properties associated with the class of the individual entities

## Integration with IoT and IIoT  <a name="integration_with_iot_and_iiot"></a>

Internet of Things (IoT) and Industrial Internet of Things (IIoT) provide a source for all sorts of measurements. However, these IoT and IIoT systems often do not understand the context from which these measurements are taken. A graph model of the plant, building, geographical area, etc is the best way to capture that context. But then we are missing the actual measurements. IntelligentGraph allows agents within the context model to pull information in from the IoT or IIoT server just-in-time, rather than pushing as much information as one can into the graph just-in-case. Since these measurements are available within the graph, just like any other asserted triple, analysis agents can also be added to the graph to create a truly intelligent graph.

## Integration with Large Language Models (LLMs) <a name="integration_with_large_language_models_llms"></a>

Clearly, IntelligentGraph can pull structured data from external systems such as IoT and merge it with the existing asserted graph. LLM (Large Language Models)  such as ChatGPT, Bard, LLama and others have opened up the possibility of merging unstructured data from the world of LLMs with the structure of graphs.

An example Jupyter/Colab notebook demonstrating its use is here: https://github.com/peterjohnlawrence/IntelligentGraph/blob/main/IntelligentGraph%2BLLM.ipynb

# Caveats <a name="caveats"></a>
- Scripts are evaluated using the Python exec() function. This can open expose you to malicious attacks if you allow open access to your intelligentGraphs.
- Is IntelligentGraph fully debugged and tested? No, but to the best of my abilities.
- IntelligentGraph does not cache retrieved results, ensuring that no results can become stale. However, this will come with a performance penalty in some cases.
