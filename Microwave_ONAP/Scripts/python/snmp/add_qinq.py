import os
from pysnmp.hlapi import *
import json
import quicksnmp
from pyconfig import *
from pysnmp.smi.rfc1902 import rfc1902
import get_qinqlinks
from aai_requests import *

def create_dict(*args):
  return dict({i:eval(i) for i in args})


def add_qinq(node,port,vlan,name=''):
    """
    inputs:
        node : Device ID
        port : S-VLAN port name
        vlan : S-VLAN value
        name : optional
    """

    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
    """
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = node))[1]
    
    already_exist=False
    """
    f=open("json/huawei/qinqlinks.json",)
    qinqlinks_hua=json.load(f)
    f.close()
    """
    URL_GET_DEVICE_QINQ_LINK = URL_GET_DEVICES +'/device/{device_id}/qinq-links'.format(device_id=node)
    qinqlinks_hua = dict()
    req_get_qinq_links = get_request(URL_GET_DEVICE_QINQ_LINK)
    if req_get_qinq_link[0] == 200 :
        qinqlinks_hua = {link['qinq-link-id']:link for link in req_get_qinq_links[1]['qinq-link']}
        

    ip = device['system-ipv4']
    id=0

    #Getting next available QinQ index
    for i in range(128):
        if str(i+1) not in qinqlinks_hua.keys() and id==0:
            id= i+1
            break
        else :
            #Checking if QinQ Link already exist
            if qinqlinks_hua[str(i+1)]['qinq-vlan-id']==vlan and qinqlinks_hua[node][str(i+1)]['port-name']==port :
                print('This Vlan is already set in this port')
                id=i+1
                already_exist=True
                break

    if id == 0 : raise ValueError('No available QinQ ID')
    values=port.split('/')
    values.append(vlan)
    if not already_exist:
        #Sending SNMP request
        quicksnmp.add_row(ip,get_qinq_row_oids(id,values),credentials)
        get_qinqlinks.update()
    return str(id)





