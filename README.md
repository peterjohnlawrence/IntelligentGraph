# IntelligentGraph
Python package that adds IntelligentGraph capabilities to RDFLib RDF graph package.

IntelligentGraph introduces a special Literal value: a SCRIPT. These literals have a datatype of SCRIPT.python.
When a SCRIPT-valued object is retrieved from the RDF store, the script is executed and the values returned from the execution of the script replace the SCRIPT-valued object.



# Documentation


# Installation
The latest release of RDFLib may be installed with Python's package management tool pip. 
Since IntelligentGraph depends on rdflib, version >7 of rdflib will be installed.
However, since IntelligentGraph is still experimental it is loaded directly from GitHub

$ pip install "git+https://github.com/peterjohnlawrence/IntelligentGraph.git"

Jupyter or Google Colab is a handy way of interacting with graphs. To install from within a cell

!pip install "git+https://github.com/peterjohnlawrence/IntelligentGraph.git"

# Getting Started

IntelligentGraph follows the same pattern as RDFLib. In fact IntelligentGraph is derived from Graph. So everything that works for RDFLib works the same for IntelligentGraph.

## Really simple start

The simplest example is to create an IntelkligentGraph with a single triple, whose value is a script that returns a literal. We don't really need a script to do this, but let's build up simply:

from rdflib import  Literal,   URIRef
from rdflib.namespace import FOAF

g = IntelligentGraph()
ig = URIRef("http://inova8.com/ig")
g.add((ig, FOAF.birthday, Literal('''_result =date(1951, 3, 8)''',datatype=SCRIPT.python)))

We can query this graph (with one triple!) as follows:

for triple in g.triples( (None , None, None)):
    print(triple)

This returns the single result:

(rdflib.term.URIRef('http://inova8.com/ig'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/birthday'), rdflib.term.Literal('1951-03-08', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date')))

Note that the script value has been replaced with a literal containing the xsd:date value that was returned from the script when it was evaluated.

## Let's get a bit more real

If we wanted to know a person's age, we could of course query this graph, and as part of the SPARQL query, or Python code handling the returned values, calculate the age in years. However, if we were to share the graph with someone, they would not have access to this code unless we shared that as well. Why not incorporate the age calculation *within* the graph





