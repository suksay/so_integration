import json
import os
import shutil
import errno
from aai_requests import *

"""
This script will copy Script/snmp/json contents to Script/snmp/static/json folder
for GUI purpose. 

Then, it also creates graph.json file for topology visualization purpose following
https://networkgeekstuff.com/networking/network-topology-visualization-example-of-using-lldp-neighborships-netconf-and-little-python-javascript/
project syntax.
"""

def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

os.chdir("Scripts/python/snmp/")

"""
f=open("json/neighborships.json",)
neighborships=json.load(f)
f.close()
f=open("json/inventory.json",)
hosts=json.load(f)
f.close()
"""
try :
    devices = get_request(URL_GET_DEVICES)[1]['device']
    neighborships = get_request(URL_GET_PHYSICAL_LINK)[1]['physical-link']
except:
    devices = list()
    neighborships = list()

graph=dict()
graph['nodes']=list()
graph['links']=list()

for ne in devices:
    node=dict()
    node['id']=ne['device-id']
    if 'huawei' in ne['vendor']:
        node['group']='4'
    elif 'nec' in ne['vendor']:
        node['group']='3'
    else: node['group']='1'

    graph['nodes'].append(node.copy())

"""
for id in neighborships.keys():
    for neigh in neighborships[id]:
        link=dict()
        link['source']=id
        if len([node for node in graph['nodes'] if node['id']==neigh['neighbor']==0]):
            node=dict()
            node['id']=neigh['neighbor']
            node['group']='1'
            graph['nodes'].append(node.copy())
        link['target']=neigh['neighbor']
        graph['links'].append(link.copy())
"""

for neigh in neighborships:
    link=dict()
    link['source'] = neigh['relationship-list']['relationship'][0]['relationship-data'][0]['relationship-value']
    link['target'] = neigh['relationship-list']['relationship']10]['relationship-data'][0]['relationship-value']

    graph['links'].append(link.copy())



with open('json/graph.json', 'w') as fp:
    json.dump(graph, fp)

shutil.rmtree('static/json')

copy('json','static/json')

print('---Done---')
