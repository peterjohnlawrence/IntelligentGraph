from rdflib.namespace import Namespace,DefinedNamespace
from rdflib import Graph, ConjunctiveGraph, Dataset, Literal, URIRef, term
from rdflib.paths import Path
from rdflib.term import Node
from typing import Generator ,Tuple,Optional,Union ,List

_SubjectType = Node
_PredicateType = Node
_ObjectType = Node
_TripleType = Tuple["_SubjectType", "_PredicateType", "_ObjectType"]
_ContextType = Graph
_TripleSelectorType = Tuple[
    Optional["_SubjectType"],
    Optional[Union["Path", "_PredicateType"]],
    Optional["_ObjectType"],
]
_TriplePathType = Tuple["_SubjectType", Path, "_ObjectType"]
_TripleOrTriplePathType= Union["_TripleType", "_TriplePathType"]

_QuadSelectorType = Tuple[
    Optional["_SubjectType"],
    Optional[Union["Path", "_PredicateType"]],
    Optional["_ObjectType"],
    Optional["_ContextType"],
]
_TripleOrQuadSelectorType = Union["_TripleSelectorType", "_QuadSelectorType"]
_TriplePathPatternType = Tuple[Optional["_SubjectType"], Path, Optional["_ObjectType"]]
_QuadPathPatternType = Tuple[
    Optional["_SubjectType"],
    Path,
    Optional["_ObjectType"],
    Optional["_ContextType"],
]
_TripleOrQuadPatternType = Union["_TriplePatternType", "_QuadPatternType"]
_OptionalQuadType = Tuple[
    "_SubjectType", "_PredicateType", "_ObjectType", Optional["_ContextType"]
]
_TriplePatternType = Tuple[
    Optional["_SubjectType"], Optional["_PredicateType"], Optional["_ObjectType"]
]
_QuadPatternType = Tuple[
    Optional["_SubjectType"],
    Optional["_PredicateType"],
    Optional["_ObjectType"],
    Optional["_ContextType"],
]
class SCRIPT(DefinedNamespace):
  """
  SCRIPT vocabulary

  The SCRIPT RDF vocabulary provides some aditional datatypes for conveniently handling scripts
  It also contains the SCRIPT evaluation engine

  Date: 2023-12-19

  """
  _fail = True
  _NS = Namespace("http://inova8.com/script/")

  python=URIRef("http://inova8.com/script/python")
  error=URIRef("http://inova8.com/script/error")

  def __init__( self):
    python_type =self.python
    error_type =self.error
    if( self.python not in  term._toPythonMapping): term.bind(self.python, str)
    if( self.error not in  term._toPythonMapping): term.bind(self.error, str)

  def _handleReturn(s,p,returnResult):
      if(returnResult is not None ):
        if(isinstance(returnResult ,Generator)):
          yield returnResult
        elif(isinstance(returnResult ,term.Node)):
          yield s, p , returnResult
        else:
          yield s, p ,Literal(returnResult)     
      else:
        yield s, p ,Literal("Error=Script does not return _return value", datatype=SCRIPT.error)  
  
  def _eval(  self,
        triple: _TriplePatternType,
        ctx :Optional[_ContextType]=None
    ) -> Generator["_TripleType", None, None]:
    s, p, o = triple
    inputs = globals()
    inputs['g']=self
    inputs['s']=s
    inputs['p']=p
    inputs['o']=o
    inputs['ctx']=ctx
    result= globals()
    result['_result']=None
    try:
      exec(o,inputs,result)
    except BaseException as err:
      yield s, p ,Literal("Error="+str(err)+ "\nCode = "+ str(o), datatype=SCRIPT.error)  
    #yield SCRIPT.handleReturn(s,p,result['_result'])
    if(result['_result'] is not None ):
      if(isinstance(result['_result'] ,Generator)):
        yield result['_result']
      elif(isinstance(result['_result'] ,term.Node)):
        yield s, p , result['_result']
      else:
        yield s, p ,Literal(result['_result'])     
    else:
      yield s, p ,Literal("Error=Script does assign _return value or value assigned is None. \nCode ="+ str(o), datatype=SCRIPT.error)  
    

  def scriptEvaluator(self,  triple: _TriplePatternType,  _ctx :Optional[_ContextType]=None):
    resultGenerator = next(SCRIPT._eval(self,triple=triple), _ctx)
    (_s,_p,_o)=triple
    if(isinstance(resultGenerator,Generator)):
      try:
        #for ( _es, _ep, _eo) in resultGenerator:
        #  yield ( _es, _ep, _eo)
        for triple in resultGenerator:
          if (isinstance(triple, tuple)):
            if ( isinstance(triple[0],term.Node) and isinstance(triple[1],term.Node) and isinstance(triple[2],term.Node) ):
              yield triple
            else:
              yield _s, _p ,Literal("Error=tuple but not all elements are term.Node"+ "\nCode = "+ str(_o), datatype=SCRIPT.error)
          else:
            yield _s, _p ,Literal("Error=incomplete tuple"+ "\nCode = "+ str(_o), datatype=SCRIPT.error)
      except BaseException as err:  
        yield _s, _p ,Literal("Error="+str(err)+ "\nCode = "+ str(_o), datatype=SCRIPT.error)  
    else:
      yield resultGenerator
      
