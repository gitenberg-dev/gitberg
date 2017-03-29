import rdflib
from datetime import datetime
from rdflib_jsonld import serializer
from .pg_rdf import unblank_node, context

# get the modified data for the htm file from PG RDF
def htm_modified(file_path):
    g=rdflib.Graph()
    try:
        g.load(file_path)
    except IOError:
        return None

    ld = serializer.from_rdf(g, context_data=context, base=None,
            use_native_types=False, use_rdf_type=False,
            auto_compact=False, startnode=None, index=False)

    graph = ld['@graph']
    nodes = {}
    for obj in graph:
        if isinstance(obj,dict):
            obj = obj.copy()
            if "@id" in obj and obj["@id"].startswith("_"):
                nodeid = obj["@id"]
                node = nodes.get(nodeid,{})
                del obj["@id"]
                node.update(obj)
                nodes[nodeid] = node
            
    # now remove the blank nodes and the files
    newnodes = []
    top = None
    for obj in unblank_node(graph,nodes):
        try:
            #
            if obj[u'@type']== u'pgterms:file':
                if unicode(obj[u'@id']).endswith('.htm'):
                    return obj[u'dcterms:modified' ][u'@value']
                
        except:
            pass
            
def htm_modified_date(file_path):
    mod = htm_modified(file_path)
    if mod:
        return datetime.strptime(mod, "%Y-%m-%dT%H:%M:%S")