import os
from pysnmp.hlapi import *
import json
import pprint
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

def create_dict(*args):
  return dict({i:eval(i) for i in args})

#Using list of keys and values and return a dictionnary
def make_dict(names,values):
    result = dict()
    for i in range(len(names)):
        result[names[i]]=values[i]
    return result

#Check similarities between two lists
def common_member(a, b): 
    a_set = set(a) 
    b_set = set(b) 
    if len(a_set.intersection(b_set)) > 0: 
        return(True)  
    return(False) 


def add_eline(node,interface_a,interface_b,name,vlans_a,vlans_b):
    """
    inputs :
        node (str) : Device ID
        interface_a (str) : First interface name. Must respect the format <Board>/255/<Port>
        interface_b (str) : Second interface name. Must respect the format <Board>/255/<Port>
        name (str) : Service name
        vlans_a (list(int)) : List of allowed C-VLAN for interface_a
        vlans_b (list(int)) : List of allowed C-VLAN for interface_b
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

    board_a,subboard_a,port_a = interface_a.split('/')
    board_b,subboard_b,port_b = interface_b.split('/')
    
    """
    f=open("json/huawei/qinqlinks.json",)
    qinqlinks_hua=json.load(f)
    f.close()
    
    f=open("json/huawei/elines.json",)
    elines=json.load(f)
    f.close()
    """
    URL_GET_DEVICE_ELINES = URL_GET_DEVICES +'/device/{device_id}?depth=all'.format(device_id=node)
    req_get_elines = get_request(URL_GET_DEVICE_ELINES)

    elines = dict()
    try:
        qinqlinks_hua = [link['qinq-link-id'] for link in req_get_qinq_links[1]['qinq-link']]
        elines['uni2uni'] = { link['link-id']:link for link in req_get_elines[1]['uni-2-unis']['uni-2-uni'] }
        elines['uni2nni'] = { link['link-id']:link for link in req_get_elines[1]['uni-2-nnis']['uni-2-nni'] }
        elines['nni2nni'] = { link['link-id']:link for link in req_get_elines[1]['nni-2-nnis']['nni-2-nni'] }

    except:
        print('Error somewhere')

    elines_entries = dict()
    try:

        uni2nni=elines['uni2nni']
        nni2nni=elines['nni2nni']
        elines=elines['uni2uni']
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
        x=str(i+1)+'.1.2'
        if str(i+1)+'.1.2' not in elines.keys() and str(i+1)+'.1.1' not in uni2nni.keys():
            if id==0:
                id= str(i+1)+'.1.2'
                if nms_id !=0:
                    break
        else:
            #Checking conflicts with other E-Line services
            if str(i+1)+'.1.1' in uni2nni.keys():
                x=str(i+1)+'.1.1'
                if (common_member(vlans_a,uni2nni[x]['vlan-list']) and uni2nni[x]['port']==interface_a) or (common_member(vlans_b,uni2nni[x]['vlan-list']) and uni2nni[x]['port']==interface_b) :
                    print('A Vlan is already set in this port')
                    get_elines.del_eline(str(i+1),node)
            elif str(i+1)+'.1.2' in elines.keys():
                if (common_member(vlans_a,elines[str(i+1)+'.1.2']['vlan-list-a']) and elines[str(i+1)+'.1.2']['port-a']==interface_a) or (common_member(vlans_a,elines[str(i+1)+'.1.2']['vlan-list-b']) and elines[str(i+1)+'.1.2']['port-b']==interface_a) or (common_member(vlans_b,elines[str(i+1)+'.1.2']['vlan-list-a']) and elines[str(i+1)+'.1.2']['port-a']==interface_b) or (common_member(vlans_b,elines[str(i+1)+'.1.2']['vlan-list-b']) and elines[str(i+1)+'.1.2']['port-b']==interface_b) :
                        print('A Vlan is already set in this port')
                        get_elines.del_eline(str(i+1),node)
        
        #Getting the next available NMS service Index
        if len([info for info in elines_entries.values() if info['nms-index']==str(i+1)])==0:
            nms_id=str(i+1)
            if id !=0:
                break
    
    #Preparing request values
    vlan_str_a=str()
    vlan_str_b=str()
    for i in range(4096):
        if str(i+1) in vlans_a: vlan_str_a=vlan_str_a+'1'
        else: vlan_str_a=vlan_str_a+'0'
        if str(i+1) in vlans_b: vlan_str_b=vlan_str_b+'1'
        else: vlan_str_b=vlan_str_b+'0'

    print('vlan_a : ', vlans_a)
    print('vlan_b : ', vlans_b)
    print("--------Before  vlan-----")
    print("vlan_str_a: ", vlan_str_a)
    print("vlan_str_b: ", vlan_str_b)
    vlan_num_a=len(vlans_a)
    vlan_num_b=len(vlans_b)
    vlan_str_a=bin2hex(vlan_str_a)
    vlan_str_b=bin2hex(vlan_str_b)

    print("--------After  vlan-----")
    print("vlan_str_a: ", vlan_str_a)
    print("vlan_str_b: ", vlan_str_b)

    var_names=['name','board_a','subboard_a','port_a','board_b','subboard_b','port_b','vlan_num_a','vlan_num_b','vlan_str_a','vlan_str_b','nms_id']
    var_values=[name,board_a,subboard_a,port_a,board_b,subboard_b,port_b,vlan_num_a,vlan_num_b,vlan_str_a,vlan_str_b,nms_id]
    input_args = make_dict(var_names,var_values)
    
    #Sending SNMP request
    quicksnmp.add_row(ip,get_uni2uni_row_oids(id,**input_args),credentials)
    get_elines.update()
