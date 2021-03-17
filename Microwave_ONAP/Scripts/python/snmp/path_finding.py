import json
import os
import argparse
from aai_requests import *

"""
#Check workspace and load data files
os.chdir("Scripts/python/snmp/")
f=open("json/neighborships.json",)
graph=json.load(f)
f.close()
"""
graph = extract_neighbords_table()


def find_all_paths(graph,start,end,path=[]):
    """
        	Python Software Foundation. (2019). Python Patterns - Implementing Graphs. Récupéré sur python.org: https://www.python.org/doc/essays/graphs/
        path finding algorithm.

        inputs:
            graph (dict) : Neighborships dictionnary
            start (str) : Start Device ID
            end (str) : End Device ID
        
        outputs:
            paths (list(list)) : List of list of nodes => List of node paths 
    """
    start = start
    end= end
    path=path+[start]
    if start == end: 
        return [path] 
    paths = []
    newpaths=[]
    for node in graph[start]:
        if node["neighbor"] not in path and node["neighbor"] in graph.keys(): 
            newpaths = find_all_paths(graph, node["neighbor"], end, path) 
        for newpath in newpaths:
            if newpath not in paths: 
                paths.append(newpath) 
    return paths
    
# start="0x346ac25f1b5c" #Must be a var in the future
# end="0x346ac21d93b9"
"""
Parsing RestCONF input args :
    "python-args":
    {
        "device_a" : "<Start device ID>",
        "device_b" : "<End device ID>"
    }
"""
parser = argparse.ArgumentParser()
parser.add_argument("inputs",help="Json args")
json_arg=parser.parse_args()
args_dict = json.loads(json_arg.inputs)
start=args_dict['device_a']
end=args_dict['device_b']


paths=find_all_paths(graph,start,end)
paths_dict= dict()
detailled_paths=dict()
detailled_paths['nodes']=dict()
paths_list=list()
truc = list()
j=0

"""
Now we're getting links information for each paths. 
"""
for path in paths:
    i=0
    print('Path '+str(j+1))
    print('-----------')
    detailled_paths=dict()
    detailled_paths['nodes']=dict()
    path_list=[]
    for node in path:
        print('Node '+str(i+1)+' : '+node)
        node_dict = dict()
        detailled_node=dict()
        if node != end:
            res=[neigh for neigh in graph[node] if neigh["neighbor"]==path[i+1]]
            node_dict['links']=res            
        else: 
            res=[neigh for neigh in graph[node] if neigh["neighbor"]==path[i-1]]
            node_dict['links']=res
        detailled_paths['nodes'][node]=node_dict.copy()

        i=i+1
    paths_list.append(detailled_paths.copy())
    j=j+1
    
paths_dict['paths']=paths_list
with open('json/paths.json', 'w') as fp:
    json.dump(paths_dict, fp)

print('---Done---')
