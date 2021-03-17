import json
from pyconfig import *
import quicksnmp
from get_vlan_nec import *
from aai_requests import *


def create_vlan(host_id, vlans_dict):
    """
    inputs :
        host_id (str) : Device ID where create VLAN
        vlans_dict (dict) : Dict of VLANs to create
    """
    
    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")

    """
    #Load Hosts List
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """

    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = host_id))[1]

    #host_info = hosts[host_id]

    _exist, _created = dict(), dict()
    host_vlans_list = get_vlans_by_host(device['system-ipv4'])

    for vlan in [*vlans_dict] :
        if vlan in [*host_vlans_list] :
            _exist[vlan] = vlans_dict[vlan]
        else :
            _created[vlan] = vlans_dict[vlan]
            #Create VLAN
            add_request = quicksnmp.add_row(device['system-ipv4'],create_nec_vlan(vlan,vlans_dict[vlan]), credentials)

    return _created, _exist

 
def assign_vlan_to_port(host_id, host_port_id, vlans_dict):
    """
    inputs :
        host_id (str) : Device ID
        host_port_id (str) : Device port ID where add VLAN
        vlans_dict (dict) : Dict of VLANs to create
    """
    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")

    """
    #Load Hosts List
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = host_id))[1]

    #host_info = hosts[host_id]

    _exist, _assign = dict(), dict()
    host_vlans_list = get_vlans_by_host(device['system-ipv4'])
    host_vlan_config = get_vlans_conf_by_host(device['system-ipv4'])
    #All config in trunk mode
    host_port_config = [str(id['vlan']) for id in host_vlan_config if str(id['port_id']) == host_port_id ]

    for vlan in [*vlans_dict] :
        if vlan in [*host_vlans_list] and (vlan not in host_port_config) :
            _assign[vlan] = vlans_dict[vlan]
            #Assign VLAN to Port
            assign_request = quicksnmp.add_row(device['system-ipv4'],assign_nec_vlan(vlan,host_port_id), credentials)
            
        else :
            _exist[vlan] = vlans_dict[vlan]

    return _assign, _exist


def remove_vlan_to_port(host_id, host_port_id, vlans_dict):
    """
    inputs :
        host_id (str) : Device ID 
        host_port_id (str) : Device port ID where remove VLAN
        vlans_dict (dict) : Dict of VLANs to remove from port
    """
    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")

    """
    #Load Hosts List
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """
    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = host_id))[1]

    #host_info = hosts[host_id]

    _unexist, _unassigned = dict(), dict()
    host_vlan_config = get_vlans_conf_by_host(device['system-ipv4'])
    #All config in trunk mode
    host_port_config = [str(id['vlan']) for id in host_vlan_config if str(id['port_id']) == host_port_id ]

    for vlan in [*vlans_dict] :
        if vlan in host_port_config :
            _unassigned[vlan] = vlans_dict[vlan]          
            #Assign VLAN to Port
            unassign_request = quicksnmp.add_row(device['system-ipv4'],remove_nec_vlan(vlan,host_port_id), credentials)
        else :
            _unexist[vlan] = vlans_dict[vlan]   #VLan unexit or don't configurate on this port
     
    return _unassigned, _unexist


def delete_vlan(host_id, vlans_dict):
    """
    inputs :
        host_id (str) : Device ID where create VLAN
        vlans_dict (dict) : Dict of VLANs to delete
    """
    
    #Check workspace and load data files
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")

    """
    #Load Hosts List
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """

    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = host_id))[1]
    #host_info = hosts[host_id]

    _unexist, _deleted = dict(), dict()
    host_vlans_list = get_vlans_by_host(device['system-ipv4'])
    host_vlan_config = get_vlans_conf_by_host(device['system-ipv4'])

    for vlan in [*vlans_dict] :
        if vlan in [*host_vlans_list] :
            ports_assign = [config for config in host_vlan_config if str(config['vlan']) == vlan]

            if ports_assign != [] :
                for port in ports_assign :
                    remove_vlan_to_port(host_id, str(port['port_id']), {vlan: vlans_dict[vlan]})

            delete_request = quicksnmp.add_row(device['system-ipv4'],delete_nec_vlan(vlan),credentials)
            _deleted[vlan] = vlans_dict[vlan]
        else :
            _unexist[vlan] = vlans_dict[vlan]
         

    return _deleted, _unexist



def configure_service(host_id, host_port_name, vlan_info) :
    """
    inputs :
        host_id (str) : Device ID 
        host_port_name (str) : Device port name
        vlan_info (dict) : {vlan_id : vlan_name}
    """
    
    """"
    f=open("json/inventory.json",)
    hosts=json.load(f)
    f.close()
    """

    #Create VLAN if note exist

    create_vlan(host_id, vlan_info)

    device = get_request(URL_GET_DEVICES+'/device/{device_id}'.format(device_id = host_id))[1]

    #Get host_port_id
    interfaces = get_host_ports_id(device['system-ipv4'])
    interfaces = {interfaces[item]:item for item in interfaces} #Show {Interface_name:interface_id}

    #Assign Vlan to Port
    assign_vlan_to_port(host_id,str(interfaces[str(host_port_name)]), vlan_info)

