import os
from pysnmp.hlapi import *
import json

import quicksnmp
from pyconfig import *
from aai_requests import *

import json
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('aai_templates/'))

qinqlink_model = env.get_template('qinq-link.json')
# os.chdir("Scripts/python/snmp/")
def update():
    """
    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    #current_qinqlinks = 
    devices = get_request(URL_GET_DEVICES)[1]['device']
    qinqlinks= dict()

    #Sending SNMP request and processing values for each huawei devices
    for node in devices :
        id = node['device-id']
        if node['vendor'] == 'huawei':
            qinq_list = list()
            qinqtable=quicksnmp.get_table(node['system-ipv4'],qinq_hua,credentials)
            for qinq_e in qinqtable:
                index=qinq_e[1][0][-1]
                board=qinq_e[1][1].prettyPrint()
                subboard=qinq_e[2][1].prettyPrint()
                port=board+'/'+subboard+'/'+qinq_e[3][1].prettyPrint()
                vlan=qinq_e[4][1].prettyPrint()
                status=qinq_e[5][1].prettyPrint()
                keys=['qinq-link-id','port-name','qinq-vlan-id','status']
                values=[str(index),port,vlan,status]
                qinq_list.append(make_dict(keys,values))
            qinqlinks[id]=qinq_list.copy()

    #AAI Operations
    for node in qinqlinks:
        #Get Current qinqlinks config in device
        current_qinqlinks = dict()
        URL_GET_DEVICE_QINQ_LINK = URL_GET_DEVICES +'/device/{device_id}/qinq-links'.format(device_id=node)
        req_get_qinq_links = get_request(URL_GET_DEVICE_QINQ_LINK)
        if req_get_qinq_links[0] == 200 :
            current_qinqlinks = { link['qinq-link-id']:link['resource-version'] for link in req_get_qinq_links[1]['qinq-link'] }

        #Create or Update a qinqlink in AAI
        for config in qinqlinks[node]:
            qinqlink_data = json.loads(qinqlink_model.render(qinq_link_id=config['qinq-link-id'],port_name=config['port-name'],qinq_vlan_id=config['qinq-vlan-id'],status=config['status']))
            if config['qinq-link-id'] in current_qinqlinks.keys:
                qinqlink_data['resource-version'] = current_qinqlinks[config['qinq-link-id']]

            URL_PUT_DEVICE_QINQ_LINK = URL_GET_DEVICE_QINQ_LINK + '/qinq-link/{qinq_link_id}'.format(qinq_link_id=config['qinq-link-id'])
            req_put_qinq_links = put_request(URL_PUT_DEVICE_QINQ_LINK, qinqlink_data)



    """        
    with open('json/huawei/qinqlinks.json', 'w') as fp:
        json.dump(qinqlinks, fp)
    """

if __name__ == "__main__":
    update()
