from rdflib import Graph, Namespace, Literal, BNode
from rdflib.namespace import NamespaceManager, RDF
import pandas as pd
import sys
import os

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
def add_rdfSubject_map(g, node, rr, rml, rdf, pred_list, obj_list):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, rdf.subject))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    for i in range (len(pred_list)):
        if(pred_list[i] == rml.quotedTriplesMap):
            g.add((bnode2, rr.parentTriplesMap, obj_list[i]))
        else:
            g.add((bnode2, pred_list[i], obj_list[i]))
    #g.add((bnode2, rr.termType, rr.BlankNode))
    
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
def add_rdfObject_map(g, node, rr, rml, rdf, pred_list, obj_list):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, rdf.object))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    for i in range (len(pred_list)):
        if(pred_list[i] == rml.quotedTriplesMap):
            g.add((bnode2, rr.parentTriplesMap, obj_list[i]))
        else:
            g.add((bnode2, pred_list[i], obj_list[i]))
    
    return g

# Function that adds relationships corresponding to outer nodes
def add_relationships(g, node, rr, rml, rdf, pred_list, obj_list, pred_obj):
    
    bnode = BNode()
    g.add((node, rr.predicateObjectMap, bnode))
    g.add((bnode, rr.predicate, pred_obj))
    bnode2 = BNode()
    g.add((bnode, rml.objectMap, bnode2))
    for i in range (len(pred_list)):
        if(pred_list[i] == rml.quotedTriplesMap):
            g.add((bnode2, rr.parentTriplesMap, obj_list[i]))
        else:
            g.add((bnode2, pred_list[i], obj_list[i]))
    
    return g

#Main function
if __name__ == '__main__': 
    
    print("Enter the RML-star file you want to transform (for instance 'file.ttl'): ")
    filename = input()
    if not os.path.isfile(filename):
        sys.exit("No such file found in your directory! Please try again!")
    
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
    
    #Detection of inner and outer Triples Maps, decision about which are turning to Blank Nodes
    main_nodes = []
    subject_of = []
    object_of = []
    relationship_maps = []
    asserted = []
    for s1, p1, o1 in g.triples((None, rdf.type, None)):
        main_nodes.append(s1)
        subject_of.append(None)
        if(o1 == rr.TriplesMap):
            asserted.append(True)
        else:
            asserted.append(False)
        for s2, p2, o2 in g.triples((s1, rml.subjectMap, None)):
             for s3, p3, o3 in g.triples((o2, None, None)):             
                 if (o3 in main_nodes):
                     subject_of[main_nodes.index(s1)] = o3
    
    for s1, p1, o1 in g.triples((None, rdf.type, None)):
        object_of.append(None)
        for s2, p2, o2 in g.triples((s1, rr.predicateObjectMap , None)):
              for s3, p3, o3 in g.triples((o2, rml.objectMap, None)):  
                  for s4, p4, o4 in g.triples((o3, None, None)):
                      if (o4 in main_nodes):
                          object_of[main_nodes.index(s1)] = o4
    
    for node in main_nodes:
        subject_node = subject_of[main_nodes.index(node)]
        object_node = object_of[main_nodes.index(node)]
        
        if (subject_node != None) and (node not in subject_of) and (asserted[main_nodes.index(node)] == True):
                
                if (asserted[main_nodes.index(subject_node)] == True):
                    if (object_of[main_nodes.index(subject_node)] == None):
                            relationship_maps.append(node)
                            
                elif (asserted[main_nodes.index(subject_node)] == False):
                    if (object_node != None):
                        relationship_maps.append(node)
    
    # #Addition of inner nodes to RML for RDF Reificated
    node_counter = 1
    for node in main_nodes:

        if(node not in relationship_maps):
            #Add node
            for s1, p1, o1 in g.triples((node, rdf.type, None)):
                new_g.add((s1,p1,rml.TriplesMap))
                
            #Add logical source
            for s1, p1, o1 in g.triples((node, rml.logicalSource, None)):
                new_g.add((s1,p1,o1))
                for s2, p2, o2 in g.triples((o1, None, None)):
                    new_g.add((s2,p2,o2))
                    
            #Add subject map 
            new_g = add_subject_map(new_g, node, node_counter, rr, rml)
            node_counter += 1
            
            #Add rdf:Statement predicate-object map
            new_g = add_rdfStatement_map(new_g, node, rr, rml, rdf)
            
            #Add rdf:subject predicate-object map
            pred_list = []
            obj_list = []
            for s1, p1, o1 in g.triples((node, rml.subjectMap, None)):
                for s2, p2, o2 in g.triples((o1, None, None)):
                    pred_list.append(p2)
                    obj_list.append(o2)
                new_g = add_rdfSubject_map(new_g, node, rr, rml, rdf, pred_list, obj_list)
            
            # #Add rdf:predicate predicate-object map
            for s1, p1, o1 in g.triples((node, rr.predicateObjectMap, None)):
                for s2, p2, o2 in g.triples((o1, rr.predicate, None)):
                    new_g = add_rdfPredicate_map(new_g, node, rr, rml, rdf, o2)
            
            #Add rdf:object predicate-object map
            pred_list = []
            obj_list = []
            for s1, p1, o1 in g.triples((node, rr.predicateObjectMap, None)):
                for s2, p2, o2 in g.triples((o1, rml.objectMap, None)):
                    for s3, p3, o3 in g.triples((o2, None, None)):
                        pred_list.append(p3)
                        obj_list.append(o3)
                new_g = add_rdfObject_map(new_g, node, rr, rml, rdf, pred_list, obj_list)

        # Add relationships corresponding 
        elif(node in relationship_maps):
            pred_list = []
            obj_list = []
            for s1, p1, o1 in g.triples((node, rdf.type, None)):
                for s2, p2, o2 in g.triples((s1, rr.predicateObjectMap, None)):
                    for s3, p3, o3 in g.triples((o2, rml.objectMap, None)):
                        for s4, p4, o4 in g.triples((o3, None, None)):
                            pred_list.append(p4)
                            obj_list.append(o4)
                    for s3, p3, o3 in g.triples((o2, rr.predicate, None)): 
                        pred_obj = o3
                    new_g = add_relationships(new_g, subject_of[main_nodes.index(node)], rr, rml, rdf, pred_list, obj_list, pred_obj)
                    
                
    #New graph serialization
    new_g.serialize("new_graph.ttl", format = "ttl")
    print("Graph generated succesfully and saved as 'new_graph.ttl'!")
