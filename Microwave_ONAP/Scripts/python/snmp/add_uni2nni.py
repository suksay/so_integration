import os
from pysnmp.hlapi import *
import json
import quicksnmp
from pyconfig import *
from pysnmp.smi.rfc1902 import rfc1902
from datetime import datetime
import binascii
import get_elines
from aai_requests import *

#Conversion method from 4096 bits string to hexa string 
def bin2hex(str1):
    str2=str()
    for i in range(4096):
        if (i+1)%4==0 and i!=0:
            str2=str2+("%X" % int(str1[i-3:i+1],2))
    return binascii.unhexlify(str2)

#Check similarities between two lists
def common_member(a, b): 
    a_set = set(a) 
    b_set = set(b) 
    if len(a_set.intersection(b_set)) > 0: 
        return(True)  
    return(False) 

def add_eline(node,interface,name,vlans,qinqid):
    """
    inputs :
        node (str) : Device ID
        interface (str) : Interface name. Must respect the format <Board>/255/<Port>
        name (str) : Service name
        vlans (list) : List of allowed C-VLAN in interface (could be a single value list)
        qinqid (int) : Bridged QinQ ID
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

    URL_GET_DEVICE_QINQ_LINK = URL_GET_DEVICES +'/device/{device_id}/qinq-links'.format(device_id=node)
    URL_GET_DEVICE_ELINES = URL_GET_DEVICES +'/device/{device_id}?depth=all'.format(device_id=node)

    req_get_elines = get_request(URL_GET_DEVICE_ELINES
    req_get_qinq_links = get_request(URL_GET_DEVICE_QINQ_LINK)

    elines = dict()
    try:
        qinqlinks_hua = [link['qinq-link-id'] for link in req_get_qinq_links[1]['qinq-link']]
        elines['uni2uni'] = { link['link-id']:link for link in req_get_elines[1]['uni-2-unis']['uni-2-uni'] }
        elines['uni2nni'] = { link['link-id']:link for link in req_get_elines[1]['uni-2-nnis']['uni-2-nni'] }
        elines['nni2nni'] = { link['link-id']:link for link in req_get_elines[1]['nni-2-nnis']['nni-2-nni'] }

    except:
        qinqlinks_hua = list()

    """
    f=open("json/huawei/elines.json",)
    elines=json.load(f)
    f.close()
    """
    elines_entries = dict()
    try:
        uni2uni=elines['uni2uni']
        uni2nni=elines['uni2nni']
        nni2nni=elines['nni2nni']

        #Aggregating every E-Lines in a single list
        elines_entries.update(uni2nni)
        elines_entries.update(nni2nni)
        elines_entries.update(uni2uni)
    except:
        uni2uni = dict()
        uni2nni = dict()
        nni2nni = dict()

    input_args = dict()
    
    ip = device['system-ipv4']
    id=0
    nms_id=0

    #Getting the next available E-Line Index
    for i in range(65535):
        x=str(i+1)+'.1.1'
        if x not in elines['uni2nni'].keys() and str(i+1)+'.1.2' not in elines['uni2uni'].keys():
            if id==0:
                id= x
                if nms_id !=0:
                    break
        else :
            #Checking conflicts with other E-Line services
            if x in elines_entries.keys():
                if common_member(vlans,elines['uni2nni'][x]['vlan-list']) and elines['uni2nni'][x]['port']==interface :
                    print('A Vlan is already set in this port')
                    get_elines.del_eline(str(i+1),node)
            elif str(i+1)+'.1.2' in uni2uni.keys():
                if (common_member(vlans,uni2uni[str(i+1)+'.1.2']['vlan-list-a']) and [uni2nni][str(i+1)+'.1.2']['port-a']==interface) or (common_member(vlans,uni2uni[str(i+1)+'.1.2']['vlan-list-b']) and [uni2uni][str(i+1)+'.1.2']['port-b']==interface) :
                    print('A Vlan is already set in this port')
                    get_elines.del_eline(str(i+1),node)
        
        #Getting the next available NMS service Index
        if len([info for info in elines_entries.values() if info['nms-index']==str(i+1)])==0:
                nms_id=str(i+1)
                if id !=0:
                    break
    
    #Checking input QinQ Links availability
    if str(qinqid) not in qinqlinks_hua:
        raise ValueError("This QinQ Link doesn't exist")
    
    #Preparing request values
    vlan_str=str()
    for i in range(4096):
        if str(i+1) in vlans: vlan_str=vlan_str+'1'
        else: vlan_str=vlan_str+'0'
    vlan_str=bin2hex(vlan_str) 
    vlan_num=len(vlans)
    board,subboard,port=interface.split('/')
    values=[board,subboard,port,name,qinqid,nms_id,vlan_num,vlan_str]
    input_args = make_dict(['board','subboard','port','name','qinqid','nms_id','vlan_num','vlan_str'],values)
    input_args['nms_id']=nms_id
    input_args['vlan_num']=vlan_num

    #Sending SNMP request
    quicksnmp.add_row(ip,get_eline_row_oids(id,**input_args),credentials)
    get_elines.update()

