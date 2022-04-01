from rdflib import Graph, Namespace, Literal, BNode
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

# Function that adds subject map 
def add_subject_map(g, node, node_counter, rr, rml):
    
    subject_name = "Variable"
    bnode = BNode()
    g.add((node, rml.subjectMap, bnode))
    g.add((bnode, rml.reference, Literal(subject_name+str(node_counter))))
    g.add((bnode, rr.termType, rr.BlankNode))
    
    return g

# Function that adds rdf:Statement predicate-object map 
def add_rdfStatement_map(g, node, rr, rml, rdf):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, rdf.type))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    g.add((bnode2, rml.reference, rdf.Statement))
    
    return g

# Function that adds rdf:subject predicate-object map 
def add_rdfSubject_map(g, node, rr, rml, rdf, reference):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, rdf.subject))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    g.add((bnode2, rml.reference, Literal(reference)))
    g.add((bnode2, rr.termType, rr.BlankNode))
    
    return g

# Function that adds rdf:predicate predicate-object map 
def add_rdfPredicate_map(g, node, rr, rml, rdf, reference):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, rdf.predicate))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    g.add((bnode2, rr.constant, reference))
    
    return g

# Function that adds rdf:object predicate-object map 
def add_rdfObject_map(g, node, rr, rml, rdf, reference):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, rdf.object))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    g.add((bnode2, rr.template, reference))
    
    return g

# Function that adds relationships corresponding to outer nodes
def add_relationships(g, node, rr, rml, rdf, pred, obj):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, pred))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    g.add((bnode2, rml.reference, Literal(obj)))
    
    return g

#Main function
if __name__ == '__main__': 
    
    print("Enter the RML-star file you want to transform (for instance 'file.ttl'): ")
    filename = input()
    
    #Test case loaded in "g", new graph in "new_g"
    g = Graph()
    new_g = Graph()
    g.parse(filename) 
    
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
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    new_g.namespace_manager.bind('rdf', rdf)
    
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
    node_counter = 1
    for node in inner_nodes:
        #Add node
        for s1, p1, o1 in g.triples((node, None, rr.TriplesMap)):
            new_g.add((s1,p1,o1))
            
        #Add logical source
        for s1, p1, o1 in g.triples((node, rml.logicalSource, None)):
            new_g.add((s1,p1,o1))
            for s2, p2, o2 in g.triples((o1, None, None)):
                new_g.add((s2,p2,o2))
                
        #Add subject map 
        new_g = add_subject_map(new_g, node, node_counter, rr, rml)
        
        #Add rdf:Statement predicate-object map
        new_g = add_rdfStatement_map(new_g, node, rr, rml, rdf)
        
        #Add rdf:subject predicate-object map
        for s1, p1, o1 in g.triples((node, rml.subjectMap, None)):
            for s2, p2, o2 in g.triples((o1, rml.reference, None)):
                new_g = add_rdfSubject_map(new_g, node, rr, rml, rdf, o2)
        
        #Add rdf:predicate predicate-object map
        for s1, p1, o1 in g.triples((node, rr.predicateObjectMap, None)):
            for s2, p2, o2 in g.triples((o1, rr.predicate, None)):
                new_g = add_rdfPredicate_map(new_g, node, rr, rml, rdf, o2)
        
        #Add rdf:object predicate-object map
        for s1, p1, o1 in g.triples((node, rr.predicateObjectMap, None)):
            for s2, p2, o2 in g.triples((o1, rml.objectMap, None)):
                for s3, p3, o3 in g.triples((o2, None, None)):
                    new_g = add_rdfObject_map(new_g, node, rr, rml, rdf, o3)
    
        #Add relationshipls corresponding to outer nodes
        for outer_node in outer_nodes:
            for s1, p1, o1 in g.triples((outer_node, None, rr.TriplesMap)):
                for s2, p2, o2 in g.triples((s1, rr.predicateObjectMap, None)):
                    for s3, p3, o3 in g.triples((o2, rml.objectMap, None)):
                        for s4, p4, o4 in g.triples((o3, rml.reference, None)):
                            obj = o4
                    for s3, p3, o3 in g.triples((o2, rr.predicate, None)): 
                        pred = o3
                    new_g = add_relationships(new_g, node, rr, rml, rdf, pred, obj)
                    
                
    #New graph serialization
    new_g.serialize("new_graph.ttl", format = "ttl")
    print("Generated graph created succesfully and saved as 'new.ttl'!")

  