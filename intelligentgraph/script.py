from rdflib.namespace import Namespace,DefinedNamespace
from rdflib import  URIRef, term

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

  def __init__( self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        python_type =self.python
        error_type =self.error
        if( self.python not in  term._toPythonMapping): term.bind(self.python, str)
        if( self.error not in  term._toPythonMapping): term.bind(self.error, str)
  
