
import os
from pysnmp.hlapi import *
import json
import pprint
import quicksnmp
from pyconfig import *
import add_nni2nni,add_qinq,add_uni2nni,add_uni2uni,get_elines,get_qinqlinks
import configure_nec
from datetime import datetime
import argparse
import re
from aai_requests import *


#Check workspace and load data files
cwd = os.getcwd()
if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
f=open("json/paths.json",)
paths=json.load(f)
f.close()

"""
f=open("json/inventory.json",)
hosts=json.load(f)
f.close()
"""

try :
  devices = get_request(URL_GET_DEVICES)[1]['device']
except:
  devices = list()
  

now = datetime.now()
name=now.strftime("%m/%d/%Y,%H:%M:%S")

def create_dict(*args):
  return dict({i:eval(i) for i in args})

"""
Retriving RestCONF input args:
  "python-args":
  {
      "device_a" : "<Start device ID>",
      "device_b" : "<End device ID>",
      "interface_a" : "<Start interface name>",
      "interface_b" : "<End interface name>",
      "vlan" : "<VLAN or list of VLAN>",
      "path_number" : "<List index (in paths.json) of the chosen path>"
  }
"""
parser = argparse.ArgumentParser()
parser.add_argument("inputs",help="Json args")
json_arg=parser.parse_args()
args_dict = json.loads(json_arg.inputs)
start_intf=args_dict['interface_a']
start_intf = re.sub('\s+', '', start_intf)
end_intf=args_dict['interface_b']
end_intf = re.sub('\s+', '', end_intf)
vlan=args_dict['vlan']
path_num=args_dict['path_number']

report=list()

#Choosing the path.
chosen_path=paths['paths'][int(path_num)-1]


"""
Sequential calls of add_<<elines>>.py, add_qinq.py and configure_nec.py scripts

Algorithm behaviour is the following one (also described in the README) :

Huawei
  Configurations are sent using SNMP (see quicksnmp.py and pyconfig.py)

  Ethernet ingress <-> Ethernet egress
    Creates a Uni-to-Uni service (add_uni2uni.py) = both interfaces as C-VLAN
  Ethernet ingress <-> Modem egress (and reciprocally)
    Creates a QinQ Link on the Modem Interface (add_qinq.py)
    Creates a Uni-to-Nni service (add_uni2nni.py) = Ethernet as C-VLAN bridged to the QinQ Link
  Modem ingress <-> Modem egress
    Creates a QinQ Link on both interfaces
    Creates a Nni-to-Nni service (add_nni2nni.py) = Bridge between both QinQ Links

NEC
Configurations are sent using SNMP in th configure_nec.py script

"""


for node,links in chosen_path['nodes'].items():

    #ip=hosts[node]['address']
    ip = get_ne_with_id(node, devices)['system-ipv4']
    links=links['links']
    link = links[0]
    #print(node,hosts[node],link)
    print(get_ne_with_id(node, devices), link)
    
    #device_a = hosts[node]
    #device_b = hosts[link['neighbor']]
    device_a = get_ne_with_id(node, devices)
    device_b = get_ne_with_id(link['neighbor'], devices)
    start_device=False
    end_device=False
    if list(chosen_path['nodes'].keys()).index(node)==0:
      ingress=start_intf
      if get_ne_with_id(node, devices)['vendor']=='huawei':
        start_intf_infos=quicksnmp.get_oids(ip,get_port_oid_hua(ingress),credentials)
        ingress_cvlan=start_intf_infos[0][1]==1
        print('Ingress_cvlan',ingress_cvlan)
      else :
        configure_nec.configure_service(node,start_intf,{str(vlan) : name})
        start_device=True

    elif list(chosen_path['nodes'].keys()).index(node)==len(list(chosen_path['nodes'].keys()))-1:
      ingress=end_intf
      if get_ne_with_id(node, devices)['vendor']=='huawei':
        start_intf_infos=quicksnmp.get_oids(ip,get_port_oid_hua(ingress),credentials)
        ingress_cvlan=start_intf_infos[0][1]==1
      else :
        configure_nec.configure_service(node,end_intf,{str(vlan) : name})
        end_device=True

    if device_a['vendor']=='huawei':
        oid = get_port_oid_hua(link['local_intf'])
        infos = quicksnmp.get_oids(device_a['system-ipv4'],oid,credentials)
        egress_cvlan= infos[0][1]==1
        egress=link['local_intf']
        type=''
        if (ingress_cvlan and not egress_cvlan):
          qinqid=add_qinq.add_qinq(node,egress,vlan)
          add_uni2nni.add_eline(node,ingress,name,[vlan],qinqid)
          type='UNI-to-NNI'
          print(type)
        elif (egress_cvlan and not ingress_cvlan):
          qinqid=add_qinq.add_qinq(node,ingress,vlan)
          add_uni2nni.add_eline(node,egress,name,[vlan],qinqid)
          type='UNI-to-NNI'
          print(type)

        elif (not ingress_cvlan and not egress_cvlan):
          qinqid_a=add_qinq.add_qinq(node,egress,vlan)
          qinqid_b=add_qinq.add_qinq(node,ingress,vlan)
          add_nni2nni.add_eline(node,name,qinqid_a,qinqid_b)
          type='NNI-to-NNI'
          print(type)
        else:
          print(ingress, egress)
          add_uni2uni.add_eline(node,ingress,egress,name,[vlan],[vlan])
          type='UNI-to-UNI'
          print(type)

    else:
      if not start_device or end_device:
        configure_nec.configure_service(node,link['local_intf'],{str(vlan) : name})



    if device_b['vendor']=='huawei':
        oid = get_port_oid_hua(link['neighbor_intf'])
        infos = quicksnmp.get_oids(device_b['system-ipv4'],oid,credentials)
        ingress_cvlan= infos[0][1]==1
        ingress=link['neighbor_intf']
    else:
      if not end_device:
        configure_nec.configure_service(link['neighbor'],link['neighbor_intf'],{str(vlan) : name})

