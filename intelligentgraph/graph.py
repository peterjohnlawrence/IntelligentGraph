from intelligentgraph.script import SCRIPT

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
class Intelligent():
    _enabled = True
    stack =None
    def handleScript(  self,
          triple: _TripleSelectorType,
          _ctx :Optional[_ContextType]=None,
          stack:Optional[Graph]=None
      ) :
        if(self.stack is None):
            self.stack=Graph()
        if (triple in self.stack):
            yield (triple[0], triple[1] ,Literal("Error=Script circular reference", datatype=SCRIPT.error) )
        else:
            self.stack.add(triple)
            for s, p, o  in self.scriptEvaluator(triple=triple,_ctx= _ctx ):
                if (isinstance(o, Literal) and (o.datatype ==  SCRIPT.python)):
                    self.handleScript(triple=(s,p,o),_ctx=_ctx, stack= self.stack )
                else:
                    yield  (s, p, o )
    def disableIntelligence(self):
        self._enabled = False
    def enableIntelligence(self):
        self._enabled = True 
    def isEnabled(self):
       return self._enabled
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
        resultGenerator = next(self._eval(triple=triple), _ctx)
        (_s,_p,_o)=triple
        if(isinstance(resultGenerator,Generator)):
            try: 
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
class IntelligentGraph(Intelligent, Graph):
    """An Intelligent RDF Graph, inherited from Graph

    Supports triples with SCRIPT-valued objects, literals of datatype SCRIPT.python. 

    Instead of returning the object literal, the Python script within that literal is executed.

    The Python script can return a scalar, which is interpreted as the node replacement value for the scipt.
    Alternatively the Pythobn scrript can yield a list of tuples.

    In the event of a script execution error, the error message os returned as the literal value of the object with datatype SCRIPT.error
    """
    def triples(
            self,
            triple: _TripleSelectorType,
        ) -> Generator[_TripleOrTriplePathType, None, None]:
            """Generator over the triple store

            Returns triples that match the given triple pattern. If triple pattern
            does not provide a context, all contexts will be searched.
            """
            s, p, o = triple
            if isinstance(p, Path):
                for _s, _o in p.eval(self, s, o):
                    yield _s, p, _o    
            else:
                for (_s, _p, _o), cg in self.store.triples((s, p, o), context=self):
                    # __store not visible so replaced with store
                    if (isinstance(_o, Literal) and (_o.datatype ==  SCRIPT.python) and (self.isEnabled())): 
                        for (ss,pp,oo) in self.handleScript((_s, _p, _o)):
                            yield (ss,pp,oo)
                    else:
                        yield _s, _p, _o

#_ContextType = IntelligentGraph

class IntelligentConjunctiveGraph(Intelligent,ConjunctiveGraph):
    def triples(
        self,
        triple_or_quad: _TripleOrQuadSelectorType,
        context: Optional[_ContextType] = None,
    ) -> Generator[_TripleOrTriplePathType, None, None]:
        """
        Iterate over all the triples in the entire conjunctive graph

        For legacy reasons, this can take the context to query either
        as a fourth element of the quad, or as the explicit context
        keyword parameter. The kw param takes precedence.
        """

        s, p, o, c = self._spoc(triple_or_quad)
        context = self._graph(context or c)

        if self.default_union:
            if context == self.default_context:
                context = None
        else:
            if context is None:
                context = self.default_context

        if isinstance(p, Path):
            if context is None:
                context = self

            for s, o in p.eval(context, s, o):
                yield s, p, o
        else:
            for (s, p, o), cg in self.store.triples((s, p, o), context=context):
              if (isinstance(o, Literal) and (o.datatype ==  SCRIPT.python) and (self.isEnabled())): 
                for (ss,pp,oo) in self.handleScript(( s, p, o),cg):
                    yield (ss,pp,oo)
              else:
                yield s, p, o

    def quads(
        self, triple_or_quad: Optional[_TripleOrQuadPatternType] = None
    ) -> Generator[_OptionalQuadType, None, None]:
        """Iterate over all the quads in the entire conjunctive graph"""

        s, p, o, c = self._spoc(triple_or_quad)

        for (s, p, o), cg in self.store.triples((s, p, o), context=c):
            for ctx in cg:
              #yield s, p, o, ctx
              if (isinstance(o, Literal) and (o.datatype ==  SCRIPT.python)):
                for (ss,pp,oo) in self.handleScript(( s, p, o),ctx):
                    yield (ss,pp,oo) 
              else:
                yield s, p, o, ctx

    def triples_choices(
        self,
        triple: Union[
            Tuple[List[_SubjectType], _PredicateType, _ObjectType],
            Tuple[_SubjectType, List[_PredicateType], _ObjectType],
            Tuple[_SubjectType, _PredicateType, List[_ObjectType]],
        ],
        context: Optional[_ContextType] = None,
    ) -> Generator[_TripleType, None, None]:
        """Iterate over all the triples in the entire conjunctive graph"""
        s, p, o = triple
        if context is None:
            if not self.default_union:
                context = self.default_context
        else:
            context = self._graph(context)
        # type error: Argument 1 to "triples_choices" of "Store" has incompatible type "Tuple[Union[List[Node], Node], Union[Node, List[Node]], Union[Node, List[Node]]]"; expected "Union[Tuple[List[Node], Node, Node], Tuple[Node, List[Node], Node], Tuple[Node, Node, List[Node]]]"
        # type error note: unpacking discards type info
        for (s1, p1, o1), cg in self.store.triples_choices((s, p, o), context=context):  # type: ignore[arg-type]
            if (isinstance(o, Literal) and (o.datatype ==  SCRIPT.python)and (self.isEnabled())): 
                for (ss,pp,oo) in self.handleScript((s1, p1, o1),cg):
                    yield (ss,pp,oo) 
            else:
              yield s1, p1, o1

class IntelligentDataset(IntelligentConjunctiveGraph): 
  None
