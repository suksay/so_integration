import json
import quicksnmp
from pysnmp import hlapi
from pyconfig import *
import os
from aai_requests import *

def get_hua_id_from_inventory(ne_id, hosts):
    for ne in hosts:
        if ne['model-customization-id'] == ne_id :
            return ne['device-id']


def get_huawei_neighbors(ip_address, hosts):
    links = []
    serie_fulloutdor = [92, 138, 151, 160]
    hosts_ids = [ne['device-id'] for ne in hosts]

    ne_serie = str(quicksnmp.get_oid(str(ip_address), hua_ne_serie,credentials)[0][-1])
    if int(ne_serie) in serie_fulloutdor:
        """
            Case of full outdor NE
        """
        if_links = quicksnmp.get_table_oids(str(ip_address),hua_link_search_table, credentials)
        for link in if_links :
            link_i = dict()
            link_i["local_int_index"]  = ""
            link_i["local_intf"] = str(link[1][-1]) +"/"+ str(link[2][-1]) +"/"+ str(link[3][-1])
            link_i["neighbor"] =  get_hua_id_from_inventory(str(link[4][-1]), hosts)
            link_i["neighbor_intf"] = str(link[5][-1]) +"/"+ str(link[6][-1]) +"/"+ str(link[7][-1])
            links.append(link_i)    

    neighbors=quicksnmp.get_table(ip_address, lldp_table_hua,credentials) #For NE Interface with LLDP
    for link in neighbors:
        link_i = dict()
        if str(link[0][1]) != "Not received":
            link_i["local_int_index"]= link[0][0][-1]
            link_i["local_intf"]= str(link[0][0][-4])+'/'+str(link[0][0][-3])+'/'+str(link[0][0][-2])
            link_i["neighbor"]= '0x'+(link[0][1].prettyPrint()).replace('-','').lower()
            neighbor=[chassis for chassis in hosts_ids if link_i["neighbor"][:-4] in chassis]
            if neighbor != [] :
                link_i["neighbor"]=neighbor[0]
                n_int = str(link[1][1]).split(' ')
                if len(n_int) == 3 : link_i["neighbor_intf"]=n_int[1]
                else : link_i["neighbor_intf"]=n_int[0]
                links.append(link_i)
    return links 

def get_nec_neighbords(ip_address, hosts):
    links = []
    neighbors=quicksnmp.get_table(ip_address, lldp_table_named_oid,credentials)
    hosts_ids = [ne['device-id'] for ne in hosts]

    for link in neighbors:
        link_i = dict()
        """
            link[0][1]  : value of lldpremChassisId 
            link[1][1]  : value of lldpremPortDesc

        """
        if str(link[1][1]) != "Not received" :
            link_i["local_int_index"]= link[0][0][-2]
            loc_port_desc='.1.0.8802.1.1.2.1.3.7.1.4.'+str(link_i["local_int_index"]) #Can't do it with MIBS because of an exceeding ValueConstraint on NEC devices
            link_i["local_intf"]= str(quicksnmp.get_oid(ip_address,loc_port_desc,credentials)[0][1])
            link_i["neighbor"]= link[0][1].prettyPrint()
            neighbor=[chassis for chassis in hosts_ids if link_i["neighbor"][:-4] in chassis]
            if neighbor != [] :
                link_i["neighbor"]=neighbor[0]
                #for exemple  if lldpremPortDesc = "FastEthernet 1/255/4 Interface"
                # n_int = str(link[1][1]).split(' ') = ['FastEthernet', '1/255/4', 'Interface']
                n_int = str(link[1][1]).split(' ')
                if len(n_int) == 3 : link_i["neighbor_intf"]=n_int[1]
                else : link_i["neighbor_intf"]=n_int[0]
                if link_i["local_intf"] != 'NMS':
                    links.append(link_i)
    return links

def get():
    #Check workspace and load data files
    """
    cwd = os.getcwd()
    if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
    f=open("json/inventory.json",)
    rows=json.load(f)
    f.close()
    """
    devices = get_request(URL_GET_DEVICES)['device']

    neighborships = dict()

    for device in devices:
        links = []
        address=device['system-ipv4']
        vendor=device['vendor']
        """
        Different SNMP processing according to vendor.
        """
        if 'nec' in vendor:
            nec_links = get_nec_neighbords(address, devices)
            links.extend(nec_links)
        if vendor=='huawei':
            hua_links = get_huawei_neighbors(address, devices)
            links.extend(hua_links)
            
        if links != [] : neighborships[id]=links 
    

    """
    for id in rows.keys():
        links = []
        address=rows[id]['address']
        vendor=rows[id]['vendor']
        """
        #Different SNMP processing according to vendor.
        """
        if 'nec' in vendor:
            nec_links = get_nec_neighbords(address, rows)
            links.extend(nec_links)
        if vendor=='huawei':
            hua_links = get_huawei_neighbors(address, rows)
            links.extend(hua_links)
            
        if links != [] : neighborships[id]=links 
    """
    #Saving neighborships
    with open('json/neighborships.json', 'w') as fp:
        json.dump(neighborships, fp)

    #print(neighborships)


