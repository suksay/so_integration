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

#Dynamic dictionnary creation method 
def create_dict(*args):
  return dict({i:eval(i) for i in args})

#Check similarities between two lists
def common_member(a, b): 
    a_set = set(a) 
    b_set = set(b) 
    if len(a_set.intersection(b_set)) > 0: 
        return(True)  
    return(False) 



def add_eline(node,name,qinqid_a,qinqid_b):
    """
    inputs :
        node (str) : Device ID
        name (str) : Service name
        qinqid_a (int) : First QinQ ID
        qinqid_b (int) : Second QinQ ID
    """
    #Check workspace
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")

    """
    #Load some files
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = node))[1]

    """
    f=open("json/huawei/qinqlinks.json",)
    qinqlinks_hua=json.load(f)
    f.close()
    """
    URL_GET_DEVICE_QINQ_LINK = URL_GET_DEVICES +'/device/{device_id}/qinq-links'.format(device_id=node)
    URL_GET_DEVICE_ELINES = URL_GET_DEVICES +'/device/{device_id}?depth=all'.format(device_id=node)

    req_get_elines = get_request(URL_GET_DEVICE_ELINES)
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
        x=str(i+1)+'.1.2'
        if x not in uni2uni.keys() and x not in nni2nni.keys() and str(i+1)+'.1.1' not in uni2nni.keys():
            if id==0:
                id= x
                if nms_id !=0:
                    break
        
        #Checking conflicts with other E-Line services
        elif x in nni2nni.keys() :
            if (nni2nni[x]['qinq-link-id-a']==qinqid_a or nni2nni[x]['qinq-link-id-a']==qinqid_b) and (nni2nni[x]['qinq-link-id-b']==qinqid_a or nni2nni[x]['qinq-link-id-b']==qinqid_b):
                raise ValueError('This Nni2Nni bridge already exist')
        if len([info for info in elines_entries.values() if info['nms-index']==str(i+1)])==0:
                nms_id=str(i+1)
                if id !=0:
                    break
    
    #Checking input QinQ Links availability
    if str(qinqid_a) not in qinqlinks_hua or str(qinqid_b) not in qinqlinks_hua:
        raise ValueError("One QinQ Link doesn't exist")

    #Creating and sending the SNMP request
    input_args = make_dict(['nms_id','qinqid_a','qinqid_b','name'],[nms_id,qinqid_a,qinqid_b,name])
    quicksnmp.add_row(ip,get_nni2nni_row_oids(id,**input_args),credentials)

    get_elines.update()

