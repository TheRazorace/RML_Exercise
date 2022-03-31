from rdflib import Graph, Namespace, Literal
from rdflib.namespace import NamespaceManager, RDF
import pandas as pd

#Function that saves all triples in a Dataframe for easy visualization
def save_triples(g):
    
    s = []
    p = []
    o = []
    for stmt in g:
        s.append(stmt[0].n3(g.namespace_manager))
        p.append(stmt[1].n3(g.namespace_manager))
        o.append(stmt[2].n3(g.namespace_manager))
        
    df = pd.DataFrame({"Subject": s, "Predicate":p, "Object":o})
    pd.set_option('display.max_columns', None)
    
    return df

#Main function
if __name__ == '__main__': 
    
    #Test case loaded in "g", new graph in "new_g"
    g = Graph()
    new_g = Graph()
    g.parse("tc1.txt") 
    
    # df = save_triples(g)
    # print(df)
    
    #Namespace statements and addition to the new graph using bind()
    rr = Namespace("http://www.w3.org/ns/r2rml#")
    new_g.namespace_manager.bind('rr', rr)
    base = Namespace("http://example.org/")
    new_g.namespace_manager.bind('', base)
    ex = Namespace("http://example/")
    new_g.namespace_manager.bind('ex', ex)
    rml = Namespace("http://semweb.mmlab.be/ns/rml#")
    new_g.namespace_manager.bind('rml', rml)
    ql = Namespace("http://semweb.mmlab.be/ns/ql#")
    new_g.namespace_manager.bind('ql', ql)
    
    #Detection of inner and outer Triples Maps of the Test Case
    main_nodes = []
    inner_nodes = []
    outer_nodes = []
    for s1, p1, o1 in g.triples((None, None, rr.TriplesMap)):
        main_nodes.append(s1)
        for s2, p2, o2 in g.triples((s1, rml.subjectMap, None)):
            for s3, p3, o3 in g.triples((o2, None, None)):
                if(o3 in main_nodes):
                    outer_nodes.append(s1) 
    for node in main_nodes:
        if node not in outer_nodes:
            inner_nodes.append(node)
    
    #Addition of inner nodes to RML for RDF Reificated
    for node in inner_nodes:
        for s1, p1, o1 in g.triples((node, None, rr.TriplesMap)):
            new_g.add((s1,p1,o1))
        for s1, p1, o1 in g.triples((node, rml.logicalSource, None)):
            new_g.add((s1,p1,o1))
            for s2, p2, o2 in g.triples((o1, None, None)):
                new_g.add((s2,p2,o2))
    
    #New graph serialization
    print(new_g.serialize(format = "ttl"))

  