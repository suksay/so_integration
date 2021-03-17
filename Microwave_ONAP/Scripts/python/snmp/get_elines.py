import os
from pysnmp.hlapi import *
import json
import quicksnmp
from pyconfig import *
import binascii
import time
from aai_requests import *
import json
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('aai_templates/'))

uni2nni_model = env.get_template('uni-2-nni.json')
uni2uni_model = env.get_template('uni-2-uni.json')
nni2nni_model = env.get_template('nni-2-nni.json')

def create_dict(*args):
  return dict({i:eval(i) for i in args})

#Conversion from hexa VLAN list to binary string
def hex2bin(str):
   bin = ['0000','0001','0010','0011',
         '0100','0101','0110','0111',
         '1000','1001','1010','1011',
         '1100','1101','1110','1111']
   aa = ''
   for i in range(len(str)):
      aa += bin[int(str[i],base=16)]
   return aa

#Conversion from binary string VLAN list to Hexa
def bin2hex(str1):
    str2=str()
    for i in range(4096):
        if (i+1)%4==0 and i!=0:
            str2=str2+("%X" % int(str1[i-3:i+1],2))
    return binascii.unhexlify(str2)

def update():
    """
    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    
    try: 
        devices = get_request(URL_GET_DEVICES)['device']
    except:
        devices = list()

    #UNI2NNI
    elines= dict()
    for node in devices :
        id = node['device-id']
        if node['vendor']=='huawei':
            eline_list = list()
            elines[id]=dict()
            elinetable=quicksnmp.get_table(node['system-ipv4'],eline_hua,credentials)
            for eline_e in elinetable:
                index='.'.join((str(eline_e[3][0][-3]),str(eline_e[3][0][-2]),str(eline_e[3][0][-1])))
                nms_index = eline_e[3][1].prettyPrint()
                name=eline_e[4][1].prettyPrint()
                board=eline_e[5][1].prettyPrint()
                subboard=eline_e[6][1].prettyPrint()
                port=eline_e[7][1].prettyPrint()
                port = '/'.join((board,subboard,port))
                vlan_list=eline_e[8][1].prettyPrint().replace('0x','')
                vlan_list=str(hex2bin(vlan_list))
                vlan_list=[str(i+1) for i in range(len(vlan_list)) if vlan_list[i] =='1']
                qinqid=eline_e[9][1].prettyPrint()
                status=eline_e[10][1].prettyPrint()
                values=[str(index), nms_index,name,port,vlan_list,qinqid,status]
                #keys=['nms_index','name','port','vlan_list','qinqid','status']
                keys=['link-id','nms-index','link-name','port','vlan-list','qinq-link-id','status']
                eline_list.append(make_dict(keys,values))
            elines[id]['uni2nni']=eline_list.copy()

    #UNI2UNI
    for node in devices :
        id = node['device-id']
        if node['vendor']=='huawei':
            eline_list = list()
            elinetable=quicksnmp.get_table(node['system-ipv4'],uni2uni_hua,credentials)
            for eline_e in elinetable:
                #Main info
                index='.'.join((str(eline_e[3][0][-3]),str(eline_e[3][0][-2]),str(eline_e[3][0][-1])))
                nms_index = eline_e[3][1].prettyPrint()
                name=eline_e[4][1].prettyPrint()
                #UNI 1
                board=eline_e[5][1].prettyPrint()
                subboard=eline_e[6][1].prettyPrint()
                port=eline_e[7][1].prettyPrint()
                port_a = '/'.join((board,subboard,port))
                vlan_list=eline_e[8][1].prettyPrint().replace('0x','')
                vlan_list=str(hex2bin(vlan_list))
                vlan_list_a=[str(i+1) for i in range(len(vlan_list)) if vlan_list[i] =='1']
                #UNI 2
                board=eline_e[9][1].prettyPrint()
                subboard=eline_e[10][1].prettyPrint()
                port=eline_e[11][1].prettyPrint()
                port_b = '/'.join((board,subboard,port))
                vlan_list=eline_e[12][1].prettyPrint().replace('0x','')
                vlan_list=str(hex2bin(vlan_list))
                vlan_list_b=[str(i+1) for i in range(len(vlan_list)) if vlan_list[i] =='1']
                #Status
                status=eline_e[13][1].prettyPrint()
                keys=['link-id','nms-index','link-name','port-a','vlan-list-a','port-b','vlan-list-b','status']
                values=[str(index),nms_index,name,port_a,vlan_list_a,port_b,vlan_list_b,status]
                eline_list.append(make_dict(keys,values))
            elines[id]['uni2uni']=eline_list.copy()

    #NNI2NNI
    for node in devices :
        id = node['device-id']
        if node['vendor']=='huawei':
            eline_list = list()
            elinetable=quicksnmp.get_table(node['system-ipv4'],nni2nni_hua,credentials)
            for eline_e in elinetable:
                #Main info
                index='.'.join((str(eline_e[3][0][-3]),str(eline_e[3][0][-2]),str(eline_e[3][0][-1])))
                nms_index = eline_e[3][1].prettyPrint()
                name=eline_e[4][1].prettyPrint()
                qinqid_a=eline_e[5][1].prettyPrint()
                qinqid_b=eline_e[6][1].prettyPrint()
                #Status
                status=eline_e[7][1].prettyPrint()
                keys=['link-id','nms-index','name','qinq-link-id-a','qinq-link-id-b','status']
                values=[str(index),nms_index,name,qinqid_a,qinqid_b,status]
                eline_list.append(make_dict(keys,values))
            elines[id]['nni2nni']=eline_list.copy()

    #AAI Operations
    for node in elines:
        #Get Current Elines
        current_elinelinks = dict()
        URL_GET_DEVICE_ELINES = URL_GET_DEVICES +'/device/{device_id}?depth=all'.format(device_id=node)
        req_get_elines = get_request(URL_GET_DEVICE_ELINES)

        try:
            current_elinelinks['uni2unis'] =  { link['link-id']:link['resource-version'] for link in req_get_elines[1]['uni-2-unis']['uni-2-uni'] }
            current_elinelinks['uni2nnis'] =  { link['link-id']:link['resource-version'] for link in req_get_elines[1]['uni-2-nnis']['uni-2-nni'] }
            current_elinelinks['nni2nnis'] =  { link['link-id']:link['resource-version'] for link in req_get_elines[1]['nni-2-nnis']['nni-2-nni'] }
        except:
            current_elinelinks['uni2unis'] = dict()
            current_elinelinks['uni2nnis'] = dict()
            current_elinelinks['nni2nnis'] = dict()
        
        #UNI2NNI
        for conf in elines[node]['uni2nni']:
            uni2nni_data = json.loads(uni2nni_model.render(link_id=conf['link-id'],nms_index=config['nms-index'],link_name=config['link-name'],port=config['port'],qinq_link_id=config['qinq-link-id'],vlan_list=config['vlan-list'],status=config['status']))
            if config['link-id'] in current_elinelinks['uni2nnis'].keys:
                uni2nni_data['resource-version'] = current_elinelinks['uni2nnis'][config['link-id']]

            URL_PUT_DEVICE_UNI2NNIS = URL_GET_DEVICE_UNI2NNIS +'/uni-2-nni/{link_id}'.format(link_id=config['link-id'])
            req_put_uni2nnis = put_request(URL_PUT_DEVICE_UNI2NNIS, uni2nni_data)

        #UNI2UNI
        for conf in elines[node]['uni2uni']:
            uni2uni_data = json.loads(uni2uni_model.render(link_id=conf['link-id'],nms_index=config['nms-index'],link_name=config['link-name'],port_a=config['port-a'],vlan_list_a=config['vlan-list-a'],port_b=config['port-b'],vlan_list_b=config['vlan-list-b'],status=config['status']))
            if config['link-id'] in current_elinelinks['uni2unis'].keys:
                uni2uni_data['resource-version'] = current_elinelinks['uni2unis'][config['link-id']]

            URL_PUT_DEVICE_UNI2UNIS = URL_GET_DEVICE_UNI2UNIS +'/uni-2-uni/{link_id}'.format(link_id=config['link-id'])
            req_put_uni2unis = put_request(URL_PUT_DEVICE_UNI2UNIS, uni2uni_data)

        #NNI2NNI
        for conf in elines[node]['nni2nni']:
            nni2nni_data = json.loads(nni2nni_model.render(link_id=conf['link-id'],nms_index=config['nms-index'],link_name=config['link-name'],qinq_link_id_a=config['qinq-link-id-a'],qinq_link_i_b=config['qinq-link-id-b'],status=config['status']))
            if config['link-id'] in current_elinelinks['nni2nnis'].keys:
                nni2nni_data['resource-version'] = current_elinelinks['nni2nnis'][config['link-id']]

            URL_PUT_DEVICE_NNI2NNIS = URL_GET_DEVICE_NNI2NNIS +'/nni-2-nni/{link_id}'.format(link_id=config['link-id'])
            req_put_nni2nnis = put_request(URL_PUT_DEVICE_NNI2NNIS, nni2nni_data)

    """
    with open('json/huawei/elines.json', 'w') as fp:
        json.dump(elines, fp)
    """

#Building binary string VLAN list from Python VLAN list 
def get_vlan_str(vlans):
    vlan_str=str()
    for i in range(4096):
        if str(i+1) in vlans: vlan_str=vlan_str+'1'
        else: vlan_str=vlan_str+'0'
    return vlan_str


def del_eline(id,node):
    """
    inputs:
        id (str) : E-Line index ( format ID.NI_ID.NI_ID | e.g : 2.1.2 )
        node (str) : Device ID

    DISCLAIMER: 
    This method won't actually delete the service, but will only set it as "Disable"
    To actually delete the service, so far you must use the NMS
    """
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
    f=open("json/huawei/elines.json",)
    elines=json.load(f)
    f.close()
    """
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    devices = get_request(URL_GET_DEVICES)[1]['device']

    input_args=dict()
    uni2uni=elines[node]['uni2uni']
    uni2nni=elines[node]['uni2nni']
    nni2nni=elines[node]['nni2nni']
    ip=get_ne_with_id(node, devices)['system-ipv4']
    
    if id+'.1.1' in uni2nni.keys():
        #id,board,subboard,port,vlan_num,vlan_str,name,qinqid,nms_id
        values=uni2nni[id+'.1.1']
        board,subboard,port=values['port'].split('/')
        vlans=values['vlan_list']
        vlan_num=len(vlans)
        vlan_str=bin2hex(get_vlan_str(vlans))
        values.pop('vlan_list',None)
        values.pop('status',None)
        values.update(make_dict(['board','subboard','port','vlan_num','vlan_str'],[board,subboard,port,vlan_num,vlan_str]))
        quicksnmp.add_row(ip,delete_eline_row_oids(id+'.1.1',**values),credentials)
        print('Uni2Nni '+id+' deleted')
    elif id+'.1.2' in uni2uni.keys():
        nms_index=uni2uni[id+'.1.2']['nms_index']
        quicksnmp.add_row(ip,delete_uni2uni_row_oids(id+'.1.2',nms_index),credentials)
    update()
    time.sleep(1)

if __name__ == "__main__":
    update()
